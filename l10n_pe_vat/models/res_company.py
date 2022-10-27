# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import models, fields, api, _
from odoo.fields import Date, Datetime
from odoo.exceptions import ValidationError, UserError, AccessError

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_api_dni_connection = fields.Selection([
        ('facturacion_electronica','Facturacion Electronica DNI'),
        ('free_api','apis.net.pe')
    ], string='Api DNI', default='free_api')
    
    l10n_pe_api_ruc_connection = fields.Selection([
        ('facturacion_electronica','Facturación Electronica RUC'),
        ('free_api','apis.net.pe')
    ], string='Api RUC', default='free_api')
