# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta

class PePaymentDate(models.Model):
    
    _inherit = "pe.payment.date"
    
    order_id = fields.Many2one("sale.order", "Order")
    