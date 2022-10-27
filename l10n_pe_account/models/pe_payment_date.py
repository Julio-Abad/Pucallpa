# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta

class PePaymentDate(models.Model):
    
    _name = "pe.payment.date"
    _description = "Peruvian Payment Date"
    
    amount = fields.Float("Amount", required = True)
    date = fields.Date("Date", required = True)
    move_id = fields.Many2one("account.move", "Invoice")
    
    def get_payment_values(self):
        res = []
        for line in self:
            res.append((0,0,{'amount':line.amount, 'date':line.date}))
        return res
    
    @api.model
    def get_payment_by_qty_date(self, vals={}):
        date_start = vals.get('pe_payment_date_start') or self.env.context.get('pe_payment_date_start') or fields.Date.context_today(self)
        date_end = vals.get('pe_payment_date_end') or self.env.context.get('pe_payment_date_end') or fields.Date.context_today(self)
        qty = vals.get('pe_payment_qty') or self.env.context.get('pe_payment_qty') or 1
        amount = vals.get('pe_payment_amount') or self.env.context.get('pe_payment_amount') or 0
        amount_part = round(amount/qty,2)
        date_vals = {}
        odate_start = date_start
        odate_end = date_end
        days = (odate_end - odate_start).days
        quote_part = int(round(days / qty, 0))
        for i in range(qty):
            if i != qty-1:
                odate_start = odate_start+timedelta(quote_part)
            else:
                odate_start = odate_end
            date_vals[i] = fields.Date.to_string(odate_start)
        res = []
        for i in range(qty):
            res.append((0,0,{'amount':amount_part, 'date':date_vals[i]}))
            amount -= amount_part
            if i == qty-2:
                amount_part = amount
        return res
        
        