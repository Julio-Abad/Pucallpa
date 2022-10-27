# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Company(models.Model):
    _inherit = "res.company"

    pe_guide_ws_url = fields.Char("Guide Web Service URL")
    