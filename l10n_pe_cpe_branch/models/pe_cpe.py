# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from base64 import b64encode, decodestring, encodebytes
from datetime import datetime, timedelta
from odoo.exceptions import Warning, UserError
import requests
import zipfile
from io import BytesIO

            
class PeCpeRC(models.Model):
    _inherit = "pe.cpe.rc"
    
    branch_id = fields.Many2one('res.company.branch', 'Branch',
                                readonly=True)
    
    def _get_branch(self, invoice_id):
        if invoice_id.branch_id:
            return {'pe_branch_code':invoice_id.branch_id.pe_branch_code or '0000', 
                    'branch_id': invoice_id.branch_id.id}
        else:
            return super(PeCpeRC, self)._get_branch(invoice_id)
    
    
class PeCpeRA(models.Model):
    _inherit = "pe.cpe.ra"    
    
    branch_id = fields.Many2one('res.company.branch', 'Branch',
                                readonly=True)
    
    def _get_branch(self, invoice_id):
        if invoice_id.branch_id.pe_branch_code:
            return {'pe_branch_code':invoice_id.branch_id.pe_branch_code or '0000', 
                    'branch_id': invoice_id.branch_id.id}
        else:
            return super(PeCpeRA, self)._get_branch(invoice_id)
    