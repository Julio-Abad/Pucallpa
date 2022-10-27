# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import  Warning

class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        for obj in self:
            if obj.partner_id.pe_doc_type == '6':
                obj.partner_id.update_document()
                if obj.partner_id.pe_condition != 'HABIDO' and obj.partner_id.pe_state != 'ACTIVO':
                    raise Warning("No se puede generar factura al cliente, no esta habilitado por SUNAT")
        return super(AccountMove, self).action_post()