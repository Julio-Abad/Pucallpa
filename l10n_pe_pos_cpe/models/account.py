# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    pe_sequence_prefix = fields.Char(compute='_compute_pe_sequence')
    pe_sequence_number = fields.Integer(compute='_compute_pe_sequence')
    pe_padding = fields.Integer(compute='_compute_pe_sequence')
    pe_is_cpe = fields.Boolean(compute = '_compute_pe_is_cpe')
    
    @api.depends('edi_format_ids')
    def _compute_pe_is_cpe(self):
        for journal_id in self:
            journal_id.pe_is_cpe = bool(journal_id.edi_format_ids.filtered(lambda j: j.code == 'pe_cpe'))
    
    def _compute_pe_sequence(self):
        for journal_id in self:
            vals = journal_id._get_pe_sequence()
            journal_id.pe_sequence_prefix = vals.get('pe_sequence_prefix', False)
            journal_id.pe_sequence_number = vals.get('pe_sequence_number', False)
            journal_id.pe_padding = vals.get('pe_padding', False)

    
    def _get_pe_sequence(self):
        self.ensure_one()
        move_id = self.env['account.move'].search([('journal_id','=',self.id)], order='id DESC', limit = 1)
        vals = {}
        if move_id:
            vals['pe_sequence_prefix'] = move_id.sequence_prefix
            vals['pe_sequence_number'] = move_id.sequence_number or 0
            vals['pe_padding'] = move_id.name and (move_id.name !='/' and len(move_id.name[len(move_id.sequence_prefix):])) or 8
        else:
            vals['pe_sequence_prefix'] = "%s-" % (self.code or '')
            vals['pe_sequence_number'] = 0
            vals['pe_padding'] = 8
        return vals
    
    def get_pe_move_name(self):
        return self._get_pe_sequence()