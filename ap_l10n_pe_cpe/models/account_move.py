# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        res = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref('ap_l10n_pe_cpe.email_template_edi_invoice', raise_if_not_found=False)
        if template:
            res['context'].update({'default_template_id': template and template.id or False})
        return res