# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PeCpeCorrect(models.TransientModel):
    _name = "pe.cpe.correct.wizard"
    
    @api.model
    def _get_invoice_ids_domain(self):
        return [('id','in', self.env['pe.cpe'].browse(self.env.context.get('active_id')).summary_ids.ids)]
    
    @api.model
    def _get_default_cpe_id(self):
        return self.env.context.get('active_id')

    cpe_id = fields.Many2one("pe.cpe", "CPE", default= _get_default_cpe_id)
    invoice_ids = fields.Many2many("account.move", "pe_cpe_correct_wizard_rel", "correct_id", "invoice_id",
                                   "Invoices", domain = lambda s: s._get_invoice_ids_domain())
    is_new = fields.Boolean("New")
    add_invoice = fields.Boolean("Add Invoice")
    
    def correct_invoices(self):
        self.ensure_one()
        if self.is_new:
            self.cpe_id.write({'name':'/'})
        if not self.add_invoice:
            self.cpe_id.summary_ids.write({'pe_condition_code':'1'})
        self.invoice_ids.write({'pe_condition_code':'2'})
        
        for invoice_id in self.cpe_id.summary_ids.filtered(lambda s: s.state in ['annul']):
            pe_summary_id=self.env['pe.cpe'].get_cpe_async("rc", invoice_id.id, True)
            invoice_id.pe_summary_id=pe_summary_id.id
            invoice_id.pe_condition_code = '3'
        self.cpe_id.write({'xml_document':False, 'state':'draft'})
        return {}