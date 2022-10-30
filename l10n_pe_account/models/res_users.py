# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = "res.users"

    pe_journal_ids = fields.Many2many("account.journal", string="Invoice Journals", domain="[('type', 'in', ['sale'])]")
    