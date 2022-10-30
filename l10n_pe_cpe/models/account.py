# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    pe_is_synchronous = fields.Boolean("Is synchronous")
    