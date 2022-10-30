# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PeCPEForm(models.TransientModel):
    
    _name = "pe.query.cpe.form"
    _description = "From CPE Query"
    
    vat = fields.Char("Vat")
    number = fields.Char("Number")
    invoice_date = fields.Date("Date Invoice")
    amount = fields.Float("Amount", digits=(12,2))
    invoice_id = fields.Many2one('account.move', "Move")
    
    @api.model
    def get_document(self, vals):
        vat = vals.get('vat') or False
        number = vals.get('number') or False
        amount_total = vals.get('amount', 0.0)
        invoice_date = vals.get('invoice_date') or False
        if vat:
            invoice_id = self.env['account.move'].sudo().search([('partner_id.vat','=',vat),('name','=',number),('amount_total','=',amount_total),
                                                          ('invoice_date','=',invoice_date),('move_type','in',['out_invoice','out_refund']),('pe_annul','=',False)])
        else:
            invoice_id = self.env['account.move'].sudo().search([('name','=',number),('amount_total','=',amount_total),
                                                          ('invoice_date','=',invoice_date),('move_type','in',['out_invoice','out_refund']),('pe_annul','=',False)])
        return invoice_id.id