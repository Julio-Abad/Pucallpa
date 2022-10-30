# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    pe_require_plate = fields.Boolean('Require Plate', help = "This Product Requires Vehicle License Plate")  
