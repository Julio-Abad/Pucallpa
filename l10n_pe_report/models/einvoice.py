#-*- coding: utf-8 -*-
#License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class einvoice_catalog_12(models.Model):
    _name = "einvoice.catalog.12"
    _description = 'Tipo de operacion'

    code = fields.Char(string='Codigo', size=4, index=True, required=True)
    name = fields.Char(string='Descripcion', size=128, index=True, required=True)

    @api.depends('code', 'name')
    def name_get(self):
        result = []
        for table in self:
            l_name = table.code and table.code + ' - ' or ''
            l_name += table.name
            result.append((table.id, l_name))
        return result