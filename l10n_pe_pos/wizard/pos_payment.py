# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_is_zero


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    def check(self):
        res = super(PosMakePayment, self).check()
        order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        if order._is_pos_order_paid() and order.reversed_order_id and order.pe_annul:
            order.reversed_order_id.state = 'paid'
            if order.reversed_order_id.account_move:
                order.reversed_order_id.account_move.button_annul()
                order.reversed_order_id.account_move = False
        return res
