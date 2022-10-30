from odoo import fields, models
import json

class PeCPESend(models.AbstractModel):
    
    _inherit = "pe.cpe.send"
    
    def get_webservice(self, cpe_id):
        soap = super(PeCPESend, self).get_webservice(cpe_id)
        if self.env.user.pe_ws_url:
            soap['url'] = self.env.user.pe_ws_url
        if self.env.user.pe_ws_user:
            soap['usuario'] = self.env.user.pe_ws_user
        if self.env.user.pe_ws_password:
            soap['clave'] = self.env.user.pe_ws_password
        return soap