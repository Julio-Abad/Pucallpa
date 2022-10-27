# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    pe_credit_note_id = fields.Many2one(comodel_name="account.journal", string="Credit Note", domain="[('type','in', ['sale', 'purchase'])]")
    pe_debit_note_id = fields.Many2one(comodel_name="account.journal", string="Debit Note", domain="[('type','in', ['sale', 'purchase'])]")
    pe_invoice_code = fields.Selection(selection="_get_pe_invoice_code", string="Invoice Type Code")
    pe_credit_invoice_code = fields.Selection(selection="_get_pe_invoice_code", string="Credit Invoice Type Code")
    pe_debit_invoice_code = fields.Selection(selection="_get_pe_invoice_code", string="Debit Invoice Type Code")
    
    pe_debit_sequence = fields.Boolean(string='Dedicated Debit Note Sequence', help="Check this box if you don't want to share the same sequence for invoices and debit notes made from this journal", default=False)
    #pe_debit_sequence_id = fields.Many2one('ir.sequence', string='Debit Note Entry Sequence',
    #    help="This field contains the information related to the numbering of the debit note entries of this journal.", copy=False)
    
    #pe_debit_sequence_number_next = fields.Integer(string='Debit Notes Next Number',
    #    help='The next sequence number will be used for the next debit note.', 
    #    compute='_compute_pe_debit_sequence_number_next',
    #    inverse='_inverse_pe_debit_sequence_number_next')
    
    @api.model
    def _get_pe_invoice_code(self):
        return self.env['pe.catalog.01'].get_selection()
    
    @api.onchange('pe_invoice_code')
    def _onchange_pe_invoice_code(self):
        if self.pe_invoice_code:
            if self.pe_invoice_code in ['01', '03']:
                self.pe_credit_invoice_code = '07'
                self.pe_debit_invoice_code = '08'
        return {}
    
    @api.depends('pe_debit_sequence_id.use_date_range', 'pe_debit_sequence_id.number_next_actual')
    def _compute_pe_debit_sequence_number_next(self):
        for journal in self:
            if journal.pe_debit_sequence_id and journal.pe_debit_sequence:
                sequence = journal.pe_debit_sequence_id._get_current_sequence()
                journal.pe_debit_sequence_number_next = sequence.number_next_actual
            else:
                journal.pe_debit_sequence_number_next = 1

    def _inverse_pe_debit_sequence_number_next(self):
        for journal in self:
            if journal.pe_debit_sequence_id and journal.pe_debit_sequence and journal.pe_debit_sequence_number_next:
                sequence = journal.pe_debit_sequence_id._get_current_sequence()
                sequence.sudo().number_next = journal.pe_debit_sequence_number_next
    
    
    def write(self, vals):
        # create the relevant refund sequence
        #if vals.get('pe_debit_sequence'):
        #    for journal in self.filtered(lambda j: j.type in ('sale', 'purchase') and not j.pe_debit_sequence_id):
        #        journal_vals = {
        #            'name': journal.name,
        #            'company_id': journal.company_id.id,
        #            'code': journal.code,
        #            'refund_sequence_number_next': vals.get('pe_debit_sequence_number_next', journal.pe_debit_sequence_number_next),
        #        }
        #        journal.pe_debit_sequence_id = self.sudo()._create_sequence(journal_vals, refund=True).id
        res = super(AccountJournal, self).write(vals)
        return res
        
    @api.model
    def create(self, vals):
        #if vals.get('type') in ('sale', 'purchase') and vals.get('pe_debit_sequence') and not vals.get('pe_debit_sequence_id'):
        #    vals.update({'pe_debit_sequence_id': self.sudo()._create_sequence(vals, refund=True).id})
        res = super(AccountJournal, self).create(vals)
        return res
    

class AccountTax(models.Model):
    _inherit = 'account.tax'

    pe_tax_type = fields.Many2one(comodel_name="pe.catalog.05", string="Tax Type")
        
    pe_tier_range = fields.Selection(selection= "_get_pe_tier_range", string="Type of System", 
                                     help="Type of system to the ISC")
    
    pe_is_charge = fields.Boolean("Charge")
    
    l10n_pe_edi_tax_code = fields.Selection(selection_add=[('7152','OTH - Impuesto al Consumo de las bolsas de plástico')])
    
    @api.model
    def _get_pe_tier_range(self):
        return self.env['pe.catalog.08'].get_selection()
    
    @api.model
    def _get_pe_tax_code(self):
        return self.env['pe.catalog.05'].get_selection()
    
    @api.onchange('pe_tax_type')
    def onchange_pe_tax_type(self):
        if self.pe_tax_type:
            self.l10n_pe_edi_tax_code = self.pe_tax_type.code
            #self.l10n_pe_edi_unece_category = self.pe_tax_type.un_ece_code
            self.description = self.pe_tax_type.name_code
        else:
            self.l10n_pe_edi_tax_code = False