# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveReversal(models.TransientModel):

    _inherit = 'account.move.reversal'
    
    pe_credit_note_code = fields.Selection(selection="_get_pe_credit_note_type", string="Credit Note Code")
    
    @api.model
    def _get_pe_credit_note_type(self):
        return self.env['pe.catalog.09'].get_selection()
    
    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversal, self)._prepare_default_reversal(move=move)
        res['ref'] = self.reason
        res['pe_credit_note_code'] = self.pe_credit_note_code
        res['pe_invoice_code'] = '07'
        res['journal_id'] = move.journal_id.pe_credit_note_id.id or self.journal_id and self.journal_id.id or move.journal_id.id
        return res