# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountEdiDocument(models.Model):
    _inherit = "account.edi.document"
    
    branch_id = fields.Many2one('res.company.branch', 'Branch',
                                related='move_id.branch_id', store=True)
    