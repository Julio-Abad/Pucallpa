# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    
    _inherit = "res.users"
    
    @api.model
    def domain_branch_ids(self):
        return [('id', 'in', self.env.user.branch_ids.ids)]
    
    branch_id = fields.Many2one('res.company.branch', 'Branch')
    branch_ids = fields.Many2many('res.company.branch', 'res_company_branch_users_rel', 'user_id', 'cid',
        string='Branches', default=lambda self: self.env.user._branch_default_get().ids)
    branches_count = fields.Integer("Branches Count", compute="_compute_branches_count", store=True)
    
    def _compute_branches_count(self):
        for user in self:
            user.branches_count = len(user.branch_ids)
    
    def _branch_default_get(self):
        return self.env.user.branch_id