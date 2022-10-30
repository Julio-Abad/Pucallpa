# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    pe_unspsc_code = fields.Char("UNSPSC Code")

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    pe_unspsc_code = fields.Char("UNSPSC Code")
    pe_product_type = fields.Selection([("discount","Discount"),
                                        ("charge","Charge"),
                                        ("prepayment", "Prepayment")], "Product")
    pe_subject_detraction = fields.Selection('_get_pe_subject_detraction', 'Subject to Detraction')

    @api.model
    def _get_pe_subject_detraction(self):
        return self.env['pe.catalog.54'].get_selection()
