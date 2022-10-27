# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    
    _inherit = "res.users"
    
    @api.model
    def domain_pe_branch_ids(self):
        partner_ids = self.env['res.company'].search([]).mapped('partner_id').ids
        return [('parent_id', 'in', partner_ids)]
    
    pe_branch_id = fields.Many2one('res.partner', 'Branch', domain = lambda self: self.domain_pe_branch_ids())
    