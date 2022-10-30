# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class UoM(models.Model):
    _inherit = 'uom.uom'
    
    pe_unit_code = fields.Selection(selection="_get_pe_unit_code", string="Unit Code")
    
    @api.model
    def _get_pe_unit_code(self):
        return self.env['pe.catalog.03'].get_selection()