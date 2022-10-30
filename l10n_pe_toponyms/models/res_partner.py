# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'
    
    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            if not self.country_id:
                self.country_id=self.state_id.country_id.id
            return {'domain': {'city_id': [('state_id', '=', self.state_id.id)]}}
        else:
            return {'domain': {'city_id': []}}
    
    
    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            if not self.state_id:
                self.state_id=self.city_id.state_id.id
            return {'domain': {'l10n_pe_district': [('city_id', '=', self.city_id.id)]}}
        else:
            return {'domain': {'l10n_pe_district': []}}
        
    @api.onchange('l10n_pe_district')
    def _onchange_l10n_pe_district(self):
        if self.l10n_pe_district:
            if not self.city_id:
                self.city_id=self.l10n_pe_district.city_id.id
            self.zip= self.l10n_pe_district.code or False
            self.city = self.l10n_pe_district.name 