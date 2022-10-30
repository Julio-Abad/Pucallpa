# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    reversed_entry_id = fields.Many2one('account.move', string="Reversal of", readonly=True, copy=False)
    reversed_order_id = fields.Many2one('pos.order', string="Reversal Order", readonly=True, copy=False)
    
    def _prepare_refund_values(self, current_session):
        res = super(PosOrder, self)._prepare_refund_values(current_session)
        self.ensure_one()
        res['reversed_entry_id'] = self.account_move.id
        res['reversed_order_id'] = self.id
        return res
    
    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        if self.reversed_entry_id:
            res['reversed_entry_id'] = self.reversed_entry_id.id
        return res
    
    