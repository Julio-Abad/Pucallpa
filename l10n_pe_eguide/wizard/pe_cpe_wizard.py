# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from librecpe import Servidor


class PeCpeWizard(models.TransientModel):
    _inherit = "pe.cpe.wizard"

    pe_guide_ws_url = fields.Char("Guide Web Service URL", required = True)
        
    @api.model
    def default_get(self, fields_list):
        values = super(PeCpeWizard, self).default_get(fields_list)
        if self.env.context['active_model'] == 'res.config.settings' and 'active_ids' in self.env.context:
            active_settings_ids = self.env['res.config.settings'].browse(self.env.context['active_ids'])
            company_id = active_settings_ids and active_settings_ids[0].company_id or False
            values['pe_guide_ws_url'] = company_id and company_id.pe_guide_ws_url or False
        return values
    
    
    def appy_configuration(self):
        self.ensure_one()
        res = super(PeCpeWizard, self).appy_configuration()
        values = {}
        values['pe_guide_ws_url'] = self.pe_guide_ws_url or False
        self.company_id.write(values)
    