# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    branch_id = fields.Many2one('res.company.branch', 'Branch', default = lambda self: self.env.user._branch_default_get())
    