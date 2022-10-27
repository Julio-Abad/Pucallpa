# -*- coding: utf-8 -*-

import base64
import logging
import os

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class CompanyBranch(models.Model):
    _inherit = "res.company.branch"
    
    pe_branch_code = fields.Char('Branch')
    pe_ws_url = fields.Char("Web Service URL")
    pe_ws_status_url = fields.Char("Web Service Status URL")
    pe_ws_user = fields.Char("User")
    pe_ws_password = fields.Char("Password")
    