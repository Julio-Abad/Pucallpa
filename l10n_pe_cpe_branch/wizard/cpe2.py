from odoo import fields, models
import json

class PeCPESend(models.AbstractModel):
    
    _inherit = "pe.cpe.send"
    
    def _get_adquirente(self, partner_id):
        return {'adquirente': self._empresa(partner_id)} 
    
    def _get_emisor(self, company_id, cpe_id = False, branch_code = False, user_id=False):
        if cpe_id and not branch_code:
            branch_code = cpe_id.branch_id.pe_branch_code
        if not branch_code and user_id:
            branch_code = user_id.branch_id.pe_branch_code or company_id.pe_branch_code
        vals = super(PeCPESend, self)._get_emisor(company_id, cpe_id, branch_code, user_id)
        if cpe_id.branch_id:
            branch_id = cpe_id.branch_id.partner_id
            vals['direccion'] = branch_id.street or ''
            vals['urbanizacion'] = branch_id.street2 or ''
            vals['ubigeo'] = branch_id.l10n_pe_district.code or ''
            vals['distrito'] = branch_id.l10n_pe_district.name or ''
            vals['provincia'] = branch_id.city_id.name or ''
            vals['region'] = branch_id.state_id.name or ''
            vals['codPais'] = branch_id.country_id.code or ''
            vals['email'] = branch_id.email or ''
        return vals
    
    def get_webservice(self, cpe_id):
        soap = super(PeCPESend, self).get_webservice(cpe_id)
        branch_id = cpe_id.branch_id
        if branch_id:
            if branch_id.pe_ws_user:
                soap['usuario'] = branch_id.pe_ws_user
            if branch_id.pe_ws_password:
                soap['clave'] = branch_id.pe_ws_password
            if branch_id.pe_ws_url:
                soap['url'] = branch_id.pe_ws_url 
            if cpe_id._name in ["pe.cpe.ra", "pe.cpe.rc"]:
                if cpe_id.pe_ticket and branch_id.pe_ws_url:
                    soap['url'] = branch_id.pe_ws_url 
                elif branch_id.pe_ws_url or branch_id.pe_ws_status_url:
                    soap['url'] = branch_id.pe_ws_url or branch_id.pe_ws_status_url
        return soap