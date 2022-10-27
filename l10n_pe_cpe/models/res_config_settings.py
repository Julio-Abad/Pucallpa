# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    pe_max_days = fields.Integer(related="company_id.pe_max_days", readonly=False,
        string='Maximum days', help="Maximum days to send electronic documents.")
    
    def action_cpe_config_wizard(self):
        self.ensure_one()
        context = dict(self.env.context)
        context['active_id'] = self.ids
        return {
            'name': _('CPE Wizard'),
            'res_model': 'pe.cpe.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_pe_cpe.view_form_pe_cpe_wizard').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }