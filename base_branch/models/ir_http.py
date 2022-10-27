# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models
from odoo.http import request
import odoo

class Http(models.AbstractModel):
    _inherit = 'ir.http'
    
    def session_info(self):
        session_info = super(Http, self).session_info()
        user = request.env.user
        session_info.update( {
            "user_branches": {'current_branches': (user.branch_id.id, user.branch_id.name), 'allowed_branches': [(comp.id, comp.name) for comp in user.branch_ids]},
            })
        return session_info 
        
    