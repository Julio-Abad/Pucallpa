# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"
    
    def _get_default_pe_invoice_code(self):
        pe_invoice_code = False
        if self.env.context.get('default_move_type','') in ['out_invoice', 'in_invoice']:
            pe_invoice_code = '01'
        if self.env.context.get('default_move_type','') in ['out_refund', 'in_refund']:
            pe_invoice_code = '07'
        return pe_invoice_code
        
    
    pe_invoice_code = fields.Selection(selection="_get_pe_invoice_code", string="Invoice Type Code", default = _get_default_pe_invoice_code,
                                       index=True, readonly=True, states={'draft': [('readonly', False)]})
    pe_debit_note_code = fields.Selection(selection="_get_pe_debit_note_type", string="Dedit Note Code",  
                                          readonly=True, states={'draft': [('readonly', False)]})
    pe_credit_note_code = fields.Selection(selection="_get_pe_credit_note_type", string="Credit Note Code", readonly=True, 
                                           states={'draft': [('readonly', False)]})
    pe_license_plate = fields.Char("License Plate", size=10, readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    
    pe_qty_fees = fields.Integer("Fees", default = 1,  readonly=True, states={'draft': [('readonly', False)]}, copy = False)
    
    pe_payment_lines = fields.One2many('pe.payment.date', 'move_id', 'Payment Lines',  readonly=True, states={'draft': [('readonly', False)]})
    
    pe_annul = fields.Boolean('Annulled', readonly=True, copy = False)

    pe_subject_detraction = fields.Selection('_get_pe_subject_detraction', 'Subject to Detraction',
                                             readonly=True, states={'draft': [('readonly', False)]})
    pe_detraction_amount = fields.Monetary('Detraction Amount', copy=False, store = True, currency_field='company_currency_id',
                                           compute="_compute_pe_detraction_amount_percentage")
    pe_detraction_percentage = fields.Float('Detraction Percentage', digits=(12, 2), copy=False, store = True,
                                            compute="_compute_pe_detraction_amount_percentage")

    pe_subject_retention = fields.Selection("_get_pe_subject_retention", "Subject to Retention", readonly=True,
                                            states={'draft': [('readonly', False)]})
    pe_retention_percentage = fields.Float('Retention Percentage', digits=(12, 2), copy=False, store=True,
                                            compute="_compute_pe_retention_amount_percentage")
    pe_retention_amount = fields.Monetary('Retention Amount', copy=False, store=True,
                                           compute="_compute_pe_retention_amount_percentage")

    @api.model
    def _get_pe_subject_retention(self):
        return self.env['pe.catalog.23'].get_selection()

    @api.depends('pe_subject_retention', 'amount_total', 'invoice_date')
    def _compute_pe_retention_amount_percentage(self):
        for move_id in self:
            amount = move_id.currency_id._convert(move_id.amount_total,
                                               move_id.env.ref('base.PEN'), move_id.company_id,
                                               move_id.invoice_date or fields.Date.context_today(self))
            if move_id.pe_subject_retention and amount>=700:
                catalog_id = self.env['pe.catalog.23'].get_by_code(move_id.pe_subject_retention)
                move_id.pe_retention_amount = catalog_id.percent * move_id.amount_total/100
                move_id.pe_retention_percentage = catalog_id.percent/100
            else:
                move_id.pe_retention_amount = 0.0
                move_id.pe_retention_percentage = 0.0

    @api.onchange('invoice_line_ids', 'invoice_line_ids.product_id', 'amount_total', 'invoice_date')
    @api.depends('invoice_line_ids', 'invoice_line_ids.product_id', 'amount_total', 'invoice_date')
    def _onchange_invoice_pe_detractions(self):
        for line_id in self.line_ids.filtered(
                lambda s: s.product_id.pe_subject_detraction and s.move_id.move_type in ['out_invoice', 'out_refund']):
            catalog_id = self.env['pe.catalog.54'].get_by_code(line_id.product_id.pe_subject_detraction)
            amount = self.currency_id._convert(self.amount_total,
                                               self.env.ref('base.PEN'), self.company_id,
                                               self.invoice_date or fields.Date.context_today(self))
            if amount > 700:
                if not self.pe_subject_detraction and catalog_id:
                    self.pe_subject_detraction = catalog_id.code
                elif self.pe_subject_detraction and catalog_id:
                    catalog2_id = self.env['pe.catalog.54'].get_by_code(self.pe_subject_detraction)
                    if catalog2_id.rate > catalog_id.rate:
                        self.pe_subject_detraction = catalog2_id.code
                self.pe_operation_type = '1001'
            else:
                self.pe_subject_detraction = False
                self.pe_operation_type = '0101'
        return {}

    @api.onchange('pe_subject_detraction')
    @api.depends('pe_subject_detraction')
    def onchange_pe_subject_detraction(self):
        amount = self.currency_id._convert(self.amount_total,
                                           self.env.ref('base.PEN'), self.company_id,
                                           self.invoice_date or fields.Date.context_today(self))
        if amount>700 and self.pe_subject_detraction:
            self.pe_operation_type = '1001'
        else:
            self.pe_operation_type = '0101'

    @api.model
    def _get_pe_subject_detraction(self):
        return self.env['pe.catalog.54'].get_selection()

    @api.depends("pe_subject_detraction", "amount_total", "invoice_date", "currency_id")
    def _compute_pe_detraction_amount_percentage(self):
        for move_id in self:
            amount_total = move_id.currency_id._convert(move_id.amount_total,
                                               self.env.ref('base.PEN'), move_id.company_id,
                                               move_id.invoice_date or fields.Date.context_today(self))
            if move_id.pe_subject_detraction and amount_total>=700:
                catalog_id = self.env['pe.catalog.54'].get_by_code(move_id.pe_subject_detraction)
                pe_detraction_percentage = round(catalog_id.rate / 100, 2)
                move_id.pe_detraction_percentage = pe_detraction_percentage
                amount = move_id.currency_id._convert(pe_detraction_percentage * move_id.amount_total,
                                                      self.env.ref('base.PEN'), move_id.company_id,
                                                      move_id.invoice_date or fields.Date.context_today(self))
                move_id.pe_detraction_amount = round(amount)
            else:
                move_id.pe_detraction_percentage = 0.0
                move_id.pe_detraction_amount = 0.0

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super(AccountMove, self)._get_last_sequence_domain(relaxed)
        if self.journal_id.pe_debit_sequence and self.pe_invoice_code in ['08']:
            where_string+= ' AND pe_invoice_code = %(pe_invoice_code)s'
            param['pe_invoice_code'] = self.pe_invoice_code
        if self.journal_id.pe_invoice_code in ['03']:
            where_string+= ' AND pe_invoice_code = %(pe_invoice_code)s'
            param['pe_invoice_code'] = self.pe_invoice_code
        return where_string, param
    
    def _l10n_pe_get_formatted_sequence(self, number=0):
        if self.is_sale_document():
            if self.journal_id.pe_invoice_code in ['01'] and self.pe_invoice_code  in ['01','07','08']:
                if self.pe_invoice_code  in ['07']:
                    return '%s-%08d' % ('FC0', number)
                elif self.pe_invoice_code  in ['08']:
                    return '%s-%08d' % ('FD0', number)
                else:
                    return '%s-%08d' % ('F00', number)
            if self.journal_id.pe_invoice_code in ['03'] and self.pe_invoice_code  in ['03','07','08']:
                if self.pe_invoice_code  in ['07']:
                    return '%s-%08d' % ('BC0', number)
                elif self.pe_invoice_code  in ['08']:
                    return '%s-%08d' % ('BD0', number)
                else:
                    return '%s-%08d' % ('B00', number)
            if self.journal_id.pe_invoice_code in ['07','08'] and self.partner_id.pe_doc_type in ['6']:
                if self.pe_invoice_code  in ['07']:
                    return '%s-%08d' % ('FC0', number)
                elif self.pe_invoice_code  in ['08']:
                    return '%s-%08d' % ('FD0', number)
            if self.journal_id.pe_invoice_code in ['07','08'] and self.partner_id.pe_doc_type not in ['6']:
                if self.pe_invoice_code  in ['07']:
                    return '%s-%08d' % ('BC0', number)
                elif self.pe_invoice_code  in ['08']:
                    return '%s-%08d' % ('BD0', number)
        return False
            
    
    def _get_starting_sequence(self):
        if self.env.company.country_id.code == "PE" and self.move_type in ['out_invoice','out_refund']:
            number = self._l10n_pe_get_formatted_sequence()
            if number:
                return number
        return super()._get_starting_sequence()

    def prepare_pe_fees_vals(self):
        self.ensure_one()
        pe_start_date = self.invoice_date_due or fields.Date.context_today(self)
        pe_payment_date_start = pe_start_date
        if self.invoice_payment_term_id and self.state == 'draft':
            date, amount = self.invoice_payment_term_id.compute(self.amount_total, date_ref=pe_start_date,
                                                                currency=self.company_id.currency_id)[0]
            pe_payment_date_end = fields.Date.from_string(date)
        else:
            pe_payment_date_end = self.invoice_date_due or fields.Date.context_today(self)
        vals = {}
        vals['pe_payment_date_start'] = pe_payment_date_start
        vals['pe_payment_date_end'] = pe_payment_date_end
        vals['pe_payment_qty'] = self.pe_qty_fees
        pe_detraction_amount = self.env.ref('base.PEN')._convert(self.pe_detraction_amount,
                                              self.currency_id, self.company_id,
                                              self.invoice_date or fields.Date.context_today(self))

        vals['pe_payment_amount'] = self.amount_total - (pe_detraction_amount + self.pe_retention_amount)
        return vals


    def generate_pe_fees(self):
        self.ensure_one()
        if self.pe_qty_fees<=0:
            raise ValidationError(_("The quotas must be greater than zero?"))
        elif self.amount_total <= 0.0:
            raise ValidationError(_("The total must be greater than zero "))
        if (self.invoice_date and self.invoice_date_due) and (self.invoice_date == self.invoice_date_due):
            raise ValidationError(_("The invoice date must be different from the due date"))
        vals = self.prepare_pe_fees_vals()
        self.pe_payment_lines.unlink()
        pe_payment_lines = self.env['pe.payment.date'].get_payment_by_qty_date(vals)
        self.pe_payment_lines = pe_payment_lines
    
    def pe_recompute_dynamic_lines(self):
        for invoice_id in self:
            invoice_id._onchange_currency()
            invoice_id._recompute_dynamic_lines(recompute_all_taxes=True)   
        return True
    
    def button_pe_annul(self):
        self = self.with_context(pe_annul_document = True)
        self.button_draft()
        self.write({'pe_annul':True})
        self.button_cancel()
        return True

    def button_draft(self):
        res = super(AccountMove, self).button_draft()
        self.write({'pe_annul':False})
        return res
    
    #def _recompute_tax_lines(self, recompute_tax_base_amount = False):
    #    context = dict(self.env.context)
    #    context['pe_show_all_taxes'] = True
    #    super(AccountMove, self.with_context(**context))._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
    
    #def action_reverse_pe_debit(self):
    #    action = self.env.ref('l10n_pe_invoice.action_view_account_move_debit').read()[0]

    #    if self.is_invoice():
    #        action['name'] = _('Debit Note')

    #    return action
    
    @api.model
    def _get_pe_debit_note_type(self):
        return self.env['pe.catalog.10'].get_selection()
    
    @api.model
    def _get_pe_credit_note_type(self):
        return self.env['pe.catalog.09'].get_selection()
    
    @api.model
    def _get_pe_invoice_code(self):
        return self.env['pe.catalog.01'].get_selection()
    
    def _get_sequence(self):
        res = super(AccountMove, self)._get_sequence()
        journal = self.journal_id
        if journal.pe_debit_sequence and self.pe_invoice_code == '08':
            return journal.pe_debit_sequence_id
        return res
    
    # def _reverse_move_vals(self, default_values, cancel=True):
    #     if self.env.context.get("is_pe_debit_note"):
    #         reverse_type_map = {
    #             'entry': 'entry',
    #             'out_invoice': 'out_invoice',
    #             'in_invoice': 'in_invoice',
    #             'in_refund': 'in_invoice',
    #             'out_refund': 'out_invoice',
    #             'out_receipt': 'out_receipt',
    #             'in_receipt': 'in_receipt',
    #         }
    #         type = default_values['type']
    #         default_values['type'] = reverse_type_map.get(self.type) or type
    #     res = super(AccountMove, self)._reverse_move_vals(default_values, cancel=cancel)
    #     return res
    #
    # # reversed_entry_id
    # def _reverse_moves(self, default_values_list=None, cancel=False):
    #     for i in range(len(default_values_list)):
    #         vals = default_values_list[i]
    #         val = {}
    #         journal_id= default_values_list[i].get('journal_id')
    #         if journal_id and not self.env.context.get("is_pe_debit_note"):
    #             journal = self.env['account.journal'].browse(journal_id)
    #             val['journal_id'] = journal.pe_credit_note_id and journal.pe_credit_note_id.id or journal.id
    #             val['pe_invoice_code'] = journal.pe_credit_note_id and journal.pe_credit_note_id.pe_invoice_code or journal.pe_invoice_code
    #             if not journal.pe_debit_note_id.pe_invoice_code and journal.refund_sequence:
    #                 val['pe_invoice_code'] =  journal.pe_credit_invoice_code
    #             #else:
    #             #    val['pe_invoice_code'] =  journal.pe_credit_note_id.pe_invoice_code
    #         elif journal_id and self.env.context.get("is_pe_debit_note"):
    #             journal = self.env['account.journal'].browse(journal_id)
    #             val['journal_id'] =  journal.pe_debit_note_id and journal.pe_debit_note_id.id or journal.id
    #             val['pe_invoice_code'] = journal.pe_debit_note_id and journal.pe_debit_note_id.pe_invoice_code or journal.pe_invoice_code
    #             if not journal.pe_debit_note_id.pe_invoice_code and journal.pe_debit_sequence:
    #                 val['pe_invoice_code'] =  journal.pe_debit_invoice_code
    #             #else:
    #             #    val['pe_invoice_code'] =  journal.pe_debit_note_id.pe_invoice_code
    #         if self.env.context.get('default_pe_credit_note_code'):
    #             val['pe_credit_note_code'] = self.env.context.get('default_pe_credit_note_code')
    #         if self.env.context.get('default_pe_debit_note_code'):
    #             val['pe_debit_note_code'] = self.env.context.get('default_pe_debit_note_code')
    #         if val:
    #             vals.update(val)
    #             default_values_list[i] = vals
    #     res = super(AccountMove, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)
    #     if self.env.context.get("is_pe_debit_note"):
    #         for move in res.with_context(check_move_validity=False):
    #             for line in move.invoice_line_ids:
    #                 line.price_unit = abs(line.price_unit)
    #                 line.recompute_tax_line = True
    #             #    if line.currency_id:
    #             #        line._onchange_currency()
    #             #move._onchange_invoice_line_ids()
    #             move._onchange_currency()   
    #             move._check_balanced()
    #     return res
    
    def _post(self, soft=True):
        for move in self:
            if move.move_type  in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund'] and not move.pe_invoice_code:
                reversed_entry_id = move.reversed_entry_id
                if reversed_entry_id and reversed_entry_id.move_type in ['out_invoice','in_invoice'] and move.move_type in ['out_refund', 'in_refund']:
                    move.pe_invoice_code = '07'
                elif reversed_entry_id and reversed_entry_id.move_type in ['out_invoice','in_invoice'] and move.move_type in ['out_invoice', 'in_invoice']:
                    move.pe_invoice_code = '08'
                elif reversed_entry_id and reversed_entry_id.move_type in ['out_refund','in_refund'] and move.move_type in ['out_invoice', 'in_invoice']:
                    move.pe_invoice_code = '08'
                elif not reversed_entry_id:                            
                    if move.partner_id.pe_doc_type == '6':
                        move.pe_invoice_code = '01'
                    else:
                        move.pe_invoice_code = '03'
            if not move.invoice_date:
                if move.is_sale_document(include_receipts=True):
                    move.invoice_date = fields.Date.context_today(self)
                    move.with_context(check_move_validity=False)._onchange_invoice_date()
                    date_due = move.invoice_date_due or fields.Date.context_today(self)
                    date_invoice = move.invoice_date or fields.Date.context_today(self)
                    if (date_due - date_invoice).days>0 and not move.pe_payment_lines:
                        move.generate_pe_fees()
                    elif (date_due - date_invoice).days<=0 and move.pe_payment_lines:
                        move.pe_payment_lines.unlink()
        res = super(AccountMove, self)._post(soft=soft)
        return res
    
    def _get_pe_default_journal(self):
        self.ensure_one()
        if self.pe_invoice_code:
            journal = self.journal_id
            type = journal.type
            journal_id = False
            if type == 'sale':
                journal_id = self.env.user.pe_journal_ids.filtered(lambda s: s.pe_invoice_code == self.pe_invoice_code)
            if not journal_id:
                journal_id = self.env['account.journal'].search([('pe_invoice_code','=',self.pe_invoice_code),
                                                                 ('type','=',type),
                                                                 ('company_id','=',self.company_id.id)], limit = 1)
            if not journal_id and self.pe_invoice_code == '07':
                journal_id = self.env['account.journal'].search([('pe_credit_invoice_code','=',self.pe_invoice_code),
                                                                 ('type','=',type), 
                                                                 ('company_id','=',self.company_id.id),
                                                                 ('refund_sequence','=',True)], limit = 1)
            elif not journal_id and self.pe_invoice_code == '08':
                journal_id = self.env['account.journal'].search([('pe_debit_invoice_code','=',self.pe_invoice_code),
                                                                 ('type','=',type), 
                                                                 ('company_id','=',self.company_id.id),
                                                                 ('pe_debit_sequence','=',True)], limit = 1)
            self.journal_id = journal_id and journal_id.id or journal.id
            
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.move_type in ['out_invoice', 'in_invoice', 'in_refund', 'out_refund']:
            if self.partner_id:
                if self.move_type in ['in_refund', 'out_refund']:
                    self.pe_invoice_code = '07'
                else:
                    if self.partner_id.pe_doc_type == '6' and self.pe_invoice_code not in ['01','08'] and not self.debit_origin_id:
                        self.pe_invoice_code = '01'
                    elif self.partner_id.pe_doc_type not in ['6'] and self.pe_invoice_code not in ['03','08'] and not self.debit_origin_id:
                        self.pe_invoice_code = '03'
                    elif self.debit_origin_id:
                        self.pe_invoice_code = '08'
            self._get_pe_default_journal()
        return res
    
    @api.onchange('pe_invoice_code')
    def _onchange_pe_invoice_code(self):
        self._get_pe_default_journal()
        return {}
            
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    pe_license_plate = fields.Char("License Plate", size=10)
    pe_type_affectation = fields.Selection(selection="_get_pe_type_affectation", string="Type of affectation")
    
    @api.model
    def _get_pe_type_affectation(self):
        return self.env['pe.catalog.07'].get_selection()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for line in self:
            pe_type_affectation = line._get_pe_type_affectation_by_tax()
            line.pe_type_affectation = pe_type_affectation
            if pe_type_affectation not in ['10','20','30','40']:
                line.discount = 100
            elif line.discount == 100:
                line.discount = 0
        return res
 
    def _get_pe_type_affectation_by_tax(self, taxes = None):
        self.ensure_one()
        tax_ids = taxes or self.tax_ids
        res = False
        if tax_ids:
            if tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['1000']):
                if tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9996']):
                    res = '11'
                else:
                    res = '10'
            elif tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9997']):
                if tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9996']):
                    res = '21'
                else:
                    res = '20'
            elif tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9998']):
                if tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9996']):
                    res = '31'
                else:
                    res = '30'
            elif tax_ids.filtered(lambda tax: tax.pe_tax_type.code in ['9995']):
                res = '40'
        return res or '10'
 
    def _get_computed_taxes(self):
        res = super(AccountMoveLine, self)._get_computed_taxes()
        if self.pe_type_affectation and self.move_id.is_sale_document(include_receipts=True):
            tax_is = self._set_free_tax(res.ids)
            res = self.env['account.tax'].browse(tax_is)
        #elif self.pe_type_affectation and self.move_id.is_purchase_document(include_receipts=True):
        return res
     
    def _set_free_tax(self, tax_ids):
        for line in self:
            res = tax_ids
            discount = 0
            if line.pe_type_affectation not in ['10', '20', '30', '40'] and line.move_id.is_sale_document(include_receipts=True):
                discount = 100
                free_tax= self.env['account.tax'].browse(tax_ids).filtered(lambda tax: tax.pe_tax_type.code == '9996')
                if not free_tax:
                    free_tax= self.env['account.tax'].search([('pe_tax_type.code', '=', '9996'),('type_tax_use','=','sale'),
                                                             ('company_id','=',line.move_id.company_id.id)], limit = 1)
                    res+=tax_ids + free_tax.ids
                else:
                    res = tax_ids
            elif line.move_id.is_sale_document(include_receipts=True):
                if  line.discount == 100:
                    discount = 0.0
                else:
                    discount = line.discount
                free_tax= self.env['account.tax'].browse(tax_ids).filtered(lambda tax: tax.pe_tax_type.code == '9996')
                if free_tax:
                    free_tax= self.env['account.tax'].browse(tax_ids).filtered(lambda tax: tax.pe_tax_type.code != '9996')
                    res = free_tax.ids
            line.discount = discount
            line.tax_ids = tax_ids
        return res
     
    @api.onchange('amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id')
    def _onchange_mark_recompute_taxes(self):
        res = super(AccountMoveLine, self)._onchange_mark_recompute_taxes()
        return res
    
    @api.onchange('pe_type_affectation')
    def _onchange_pe_affectation_code(self):
        for line in self:
            if line.pe_type_affectation and line.move_id.is_sale_document(include_receipts=True):
                if line.pe_type_affectation in ['10', '11', '12', '13', '14', '15', '16', '17']:
                    ids = line.tax_ids.filtered(lambda tax: tax.pe_tax_type.code == '1000')
                    if not ids:
                        ids+= self.env['account.tax'].search([('pe_tax_type.code', '=', '1000'),('type_tax_use','=','sale'),
                                                             ('company_id','=',line.move_id.company_id.id)], limit = 1)
                    
                    tax_ids = line._set_free_tax(ids.ids)                    
                elif line.pe_type_affectation in ['20', '21']:
                    ids = line.tax_ids.filtered(lambda tax: tax.pe_tax_type.code == '9997')
                    if not ids:
                        ids+= self.env['account.tax'].search([('pe_tax_type.code', '=', '9997'),('type_tax_use','=','sale'),
                                                             ('company_id','=', line.move_id.company_id.id)], limit = 1)
                     
                    tax_ids = self._set_free_tax(ids.ids)
                elif self.pe_type_affectation in ['30', '31', '32', '33', '34', '35', '36']:
                    ids = self.tax_ids.filtered(lambda tax: tax.pe_tax_type.code == '9998').ids
                    res= self.env['account.tax'].search([('pe_tax_type.code', '=', '9998'), ('id', 'in', ids)])
                    if not res:
                        res= self.env['account.tax'].search([('pe_tax_type.code', '=', '9998'),('type_tax_use','=','sale'),
                                                             ('company_id','=',self.move_id.company_id.id)], limit = 1)
                     
                    tax_ids = self._set_free_tax(ids+res.ids)
                     
                elif self.pe_type_affectation in ['40']:
                    ids = self.tax_ids.filtered(lambda tax: tax.pe_tax_type.code == '9995').ids
                    res= self.env['account.tax'].search([('pe_tax_type.code', '=', '9995'), ('id', 'in', ids)])
                    if not res:
                        res= self.env['account.tax'].search([('pe_tax_type.code', '=', '9995'),('type_tax_use','=','sale'),
                                                             ('company_id','=',self.move_id.company_id.id)], limit = 1)
                     
                    tax_ids = self._set_free_tax(ids+res.ids)

