# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    pe_credit_note_code = fields.Selection(selection="_get_pe_credit_note_type", string="Credit Note Code")
    pe_annul = fields.Boolean("Annul")
    
    @api.model
    def _get_pe_credit_note_type(self):
        return self.env['pe.catalog.09'].get_selection()
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        return res
    
    def _get_pe_type_affectation_by_tax(self, taxes = None):
        self.ensure_one()
        tax_ids = taxes
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
        return res
    
    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        if res.get('tax_ids', []):
            taxes = self.env['account.tax'].browse(res.get('tax_ids', [])[0][-1])
            res['pe_type_affectation'] = self._get_pe_type_affectation_by_tax(taxes)
        else:
            res['pe_type_affectation'] = '10'
        return res
    
    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        #res['pe_credit_note_code'] = self.pe_credit_note_code or False
        #res['pe_invoice_date'] = self.pe_invoice_date or False
        if not self.reversed_entry_id:
            if self.partner_id.pe_doc_type == '6':
                res['pe_invoice_code'] = '01'
            else:
                res['pe_invoice_code'] = '03'
        else:
            res['pe_invoice_code'] = '07'
        if self.pe_credit_note_code and self.reversed_entry_id:
            res['pe_credit_note_code'] = self.pe_credit_note_code
        return res

    def refund(self):
        res = super(PosOrder, self).refund()
        if res.get('res_id') and self:
            order_id = self.browse(res.get('res_id'))
            order_id.invoice_journal = self[0].invoice_journal.pe_credit_note_id.id or self[0].invoice_journal.id
            #order_id.reversed_order_id = self[0].id
        return res
    
    def action_annul(self):
        refund_orders = self.env['pos.order']
        for order in self:
            current_session = order.session_id.config_id.current_session_id
            if not current_session:
                raise UserError(_('To return product(s), you need to open a session in the POS %s') % order.session_id.config_id.display_name)
            refund_order = order.copy({
                'name': order.name + _(' REFUND'),
                'session_id': current_session.id,
                'date_order': fields.Datetime.now(),
                'pos_reference': order.pos_reference,
                'lines': False,
                'amount_tax': -order.amount_tax,
                'amount_total': -order.amount_total,
                'amount_paid': 0,
                'reversed_order_id': order.id,
                'reversed_entry_id': False,
                'invoice_journal': False
            })
            for line in order.lines:
                PosOrderLineLot = self.env['pos.pack.operation.lot']
                for pack_lot in line.pack_lot_ids:
                    PosOrderLineLot += pack_lot.copy()
                line.copy({
                    'name': line.name + _(' REFUND'),
                    'qty': -line.qty,
                    'order_id': refund_order.id,
                    'price_subtotal': -line.price_subtotal,
                    'price_subtotal_incl': -line.price_subtotal_incl,
                    'pack_lot_ids': PosOrderLineLot,
                    })
            refund_orders |= refund_order

        return {
            'name': _('Return Products'),
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': refund_orders.ids[0],
            'view_id': False,
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
    
    