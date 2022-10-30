# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'
    
    pe_debit_note_code = fields.Selection(selection="_get_pe_debit_note_type", string="Dedit Note Code")
    
    @api.model
    def _get_pe_debit_note_type(self):
        return self.env['pe.catalog.10'].get_selection()
    
    def _prepare_default_values(self, move):
        default_values = super(AccountDebitNote, self)._prepare_default_values(move)
        default_values['pe_debit_note_code'] = self.pe_debit_note_code
        default_values['pe_invoice_code'] = '08'
        default_values['journal_id'] = move.journal_id.pe_debit_note_id.id or self.journal_id and self.journal_id.id or move.journal_id.id
        return default_values