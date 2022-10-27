# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    def _render_template(self, template, values=None):
        if values:
            user = self.env['res.users'].browse(self.env.uid)
            res_branch = user.branch_id
            values.update({'res_branch':res_branch})
        return super(ReportAction, self)._render_template(template, values)