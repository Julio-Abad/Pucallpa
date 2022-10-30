from odoo import models, fields, api

class Country(models.Model):
    _inherit = 'res.country'
    
    pe_le_country_code = fields.Selection("_get_pe_le_country_code", "PLE Country Code")

    @api.model
    def _get_pe_le_country_code(self):
        return self.env['pe.table.35'].get_selection()