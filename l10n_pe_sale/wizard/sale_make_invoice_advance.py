# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
        if order.partner_id.pe_doc_type == '6':
            res['pe_invoice_code'] = '01'
        else:
            res['pe_invoice_code'] = '03'
        res['journal_id'] = order._get_pe_default_journal(res)
        invoice_line_ids = res.get('invoice_line_ids')
        if invoice_line_ids:
            val = invoice_line_ids[0][2]
            val['pe_type_affectation'] = so_line._get_pe_type_affectation_by_tax()
            invoice_line_ids = [(0, 0, val)]
        res['invoice_line_ids'] = invoice_line_ids
        return res
    