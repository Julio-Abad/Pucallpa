# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    pe_auto_journal_select = fields.Boolean("Auto Journal Select")
    pe_journal_ids = fields.Many2many("account.journal", string="Invoice Sale Journals", domain="[('type', 'in', ['sale']),('company_id', '=', company_id)]")
    
    # pe_default_journal_ids = fields.Many2many("account.journal", string="Invoice Sale Journals", compute = '_compute_pe_default_journal_ids')
    #
    # def _compute_pe_default_journal_ids(self):
    #     for config in self:
    #         continue
    
    