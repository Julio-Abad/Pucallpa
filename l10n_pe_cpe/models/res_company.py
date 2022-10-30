# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from librecpe import Servidor

class Company(models.Model):
    _inherit = "res.company"
    
    
    pe_is_sync = fields.Boolean("Is Synchronous", default= True)
    
    pe_ws_server = fields.Selection(Servidor().getServidores(), "Server")
    pe_ws_type = fields.Selection([("development","Development"),
                                   ('production','Production')], "Server Type")
    pe_ws_url = fields.Char("Web Service URL")
    pe_ws_status_url = fields.Char("Web Service Status URL")
    pe_ws_user = fields.Char("User")
    pe_ws_password = fields.Char("Password")
    
    pe_private_key = fields.Text("Private key")
    pe_public_key = fields.Text("Public key")
    
    
    pe_resolution_type= fields.Char("Resolution Type")
    pe_resolution_number= fields.Char("Resolution Number")
    pe_branch_code = fields.Char("Branch Code", default="0000")
    pe_max_amount = fields.Float("Maximum Amount", default = 700, digits=(12,2), help="Maximum billing limit for anonymous customers")
    pe_is_exonerated = fields.Boolean("Exonerated")
    
    pe_max_days = fields.Integer("Maximum days", default=7)
    pe_detraction_account_number = fields.Char("Detraction Account Number")