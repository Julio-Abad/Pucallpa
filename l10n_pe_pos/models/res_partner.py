# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
import requests

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def create_from_ui(self, partner):
        if partner.get('pe_last_update',False):
            last_update = partner.get('pe_last_update',False)
            if len(last_update)==27:
                pe_last_update = fields.Datetime.context_timestamp(self, datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S.%fZ')) or False
                partner['pe_last_update'] = pe_last_update
        if partner.get('pe_is_validate',False):
            if partner.get('pe_is_validate',False)=='true':
                partner['pe_is_validate'] = True
            else:
                partner['pe_is_validate'] = False 
        if not partner.get('pe_state',False):
            partner['pe_state'] = 'ACTIVO'
        if not partner.get('pe_condition',False):
            partner['pe_condition'] = 'HABIDO'
        if partner.get('pe_doc_type',False) and partner.get('pe_doc_type',False)=='6':
            partner['company_type']="company"
        # if partner.get('l10n_pe_district'):
        #    district = self.sudo().env['l10n_pe.res.city.district'].browse([partner.get('l10n_pe_district')])
        #    partner['city_id'] = district.city_id.id
        #    partner['state_id'] = district.city_id.state_id.id
        res = super(ResPartner, self).create_from_ui(partner)
        #self.browse(res).update_document()
        return res
