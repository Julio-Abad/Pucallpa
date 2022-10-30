# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class PosOrder(models.Model):
    _inherit = "pos.order"

    #pe_license_plate = fields.Char("License Plate", size=10)
    #pe_invoice_date = fields.Datetime("Invoice Date Time", copy = False)
    pe_journal_id = fields.Many2one('account.journal', string='Invoice Journal',   states={'draft': [('readonly', False)]}, readonly=True, 
                                       domain="[('type', 'in', ['sale']),('company_id','=',company_id)]", copy=True)
    pe_move_name = fields.Char(string='Move Name', readonly=True, copy=False)
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['pe_move_name']=ui_order.get('pe_move_name', False)
        res['pe_journal_id']=ui_order.get('pe_journal_id', False)
        #res['pe_invoice_date']=ui_order.get('pe_invoice_date', False)
        return res
    
    
    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        # if self.partner_id.pe_doc_type == '6':
        #     journal_ids = self.session_id.config_id.pe_journal_ids.filtered(lambda s: s.pe_invoice_code == '01')
        #     if journal_ids:
        #         res['journal_id'] = journal_ids[0].id
        #     else:
        #         journal_id = self.env['account.journal'].search([('type','=','sale'),('company_id','=',self.company_id.id),
        #                                                          ('pe_invoice_code','=','01')], limit=1)
        #         if journal_id:
        #             res['journal_id'] = journal_id.id
        # else:
        #     journal_ids = self.session_id.config_id.pe_journal_ids.filtered(lambda s: s.pe_invoice_code == '03')
        #     if journal_ids:
        #         res['journal_id'] = journal_ids[0].id
        #     else:
        #         journal_id = self.env['account.journal'].search([('type','=','sale'),('company_id','=',self.company_id.id),
        #                                                          ('pe_invoice_code','=','03')], limit=1)
        #         if journal_id:
        #             res['journal_id'] = journal_id.id
        if self.pe_move_name:
            res['name'] = self.pe_move_name
        if self.pe_journal_id:
            res['journal_id'] = self.pe_journal_id.id
        return res
    
    def get_pe_invoice_from_ui(self):
        self.ensure_one()
        vals = {}
        name = ''
        if self.account_move.pe_invoice_code in ['01']:
            name+='Factura '
        if self.account_move.pe_invoice_code in ['03']:
            name+='Boleta de venta '
        if self.account_move.pe_invoice_code in ['07']:
            name+='Nota de crédito '
        if self.account_move.pe_invoice_code in ['08']:
            name+='Nota de débito '
        if self.account_move.pe_is_cpe:
            name+='Electronica'
        vals['pe_move_name'] = self.account_move.name
        vals['pe_invoice_name'] = name
        if self.account_move.pe_is_cpe:
            vals['pe_qr_code'] = 'data:image/png;base64,%s' % str(self.account_move.pe_qr_code)
        else:
            vals['pe_qr_code'] = False
        return vals