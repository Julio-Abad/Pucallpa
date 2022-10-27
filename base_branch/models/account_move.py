# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get('default_company_id', self.env.company.id)
        branch_id = self._context.get('default_branch_id', self.env.user._branch_default_get().id)
        domain = [('company_id', '=', company_id), ('branch_id','=',branch_id), ('type', 'in', journal_types)]
        journal = None
        if self._context.get('default_currency_id'):
            currency_domain = domain + [('currency_id', '=', self._context['default_currency_id'])]
            journal = self.env['account.journal'].search(currency_domain, limit=1)
        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)
        if not journal:
            journal = super(AccountMove, self)._search_default_journal(journal_types)
        return journal
    
    @api.depends('journal_id')
    def _compute_branch_id(self):
        for move in self:
            move.branch_id = move.journal_id.branch_id or self.env.user._branch_default_get()

    branch_id = fields.Many2one('res.company.branch', 'Branch',
                                store=True, readonly=True, 
                                compute='_compute_branch_id')
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    branch_id = fields.Many2one('res.company.branch', 'Branch', related="move_id.branch_id", store=True)
    
    
