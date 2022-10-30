# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class Currency(models.Model):
    _inherit = 'res.currency'
    
    pe_currency_code = fields.Selection('_get_pe_invoice_code', "Currrency Code")
    
    @api.model
    def _get_pe_invoice_code(self):
        return self.env['pe.catalog.02'].get_selection()
    
    def is_zero(self, amount):
        if self.env.context.get('pe_show_all_taxes'):
            return False
        return  super(Currency, self).is_zero(amount)