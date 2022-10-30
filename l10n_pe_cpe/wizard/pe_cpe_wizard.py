# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from librecpe import Servidor


class PeCpeWizard(models.TransientModel):
    _name = "pe.cpe.wizard"
    _description = "CPE Wizard"
    
    
    pe_ws_server = fields.Selection(Servidor().getServidores(), "Server", required = True)
    pe_ws_type = fields.Selection([("development","Development"),
                                   ('production','Production')], "Server Type", required = True)
    pe_ws_url = fields.Char("Web Service URL", required = True)
    pe_ws_status_url = fields.Char("Web Service Status URL")
    pe_ws_user = fields.Char("User")
    pe_ws_password = fields.Char("Password/Token", required = True)
    
    pe_private_key = fields.Text("Private key")
    pe_public_key = fields.Text("Public key")
    
    #invoice_journal_id = fields.Many2one("account.journal", "Invoice Journal", domain="[('type','=','sale')]")
    #voucher_journal_id = fields.Many2one("account.journal", "Voucher Journal", domain="[('type','=','sale')]")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required = True,
                                 readonly=True)
    
    # @api.onchange('pe_ws_type','pe_ws_server')
    # def _onchange_pe_ws_server(self):
    #     if self.pe_ws_server == 'sunat' and self.pe_ws_type == 'development':
    #         self.pe_ws_url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
    #         self.pe_ws_status_url = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService?wsdl"
    #         self.pe_ws_user = "MODDATOS"
    #         self.pe_ws_password = "moddatos"
    #     elif self.pe_ws_server == 'sunat' and self.pe_ws_type == 'production':
    #         self.pe_ws_url = "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService?wsdl"
    #         self.pe_ws_status_url = "https://e-factura.sunat.gob.pe/ol-it-wsconscpegem/billConsultService?wsdl"
    #

    @api.model
    def default_get(self, fields_list):
        values = super(PeCpeWizard, self).default_get(fields_list)
        if self.env.context['active_model'] == 'res.config.settings' and 'active_ids' in self.env.context:
            active_settings_ids = self.env['res.config.settings'].browse(self.env.context['active_ids'])
            company_id = active_settings_ids and active_settings_ids[0].company_id or False
            values['pe_ws_server'] = company_id and company_id.pe_ws_server or False
            values['pe_ws_type'] = company_id and company_id.pe_ws_type or False
            values['pe_ws_url'] = company_id and company_id.pe_ws_url or False
            values['pe_ws_status_url'] = company_id and company_id.pe_ws_status_url or False
            values['pe_ws_user'] = company_id and company_id.pe_ws_user or False
            values['pe_ws_password'] = company_id and company_id.pe_ws_password or False
            values['pe_private_key'] = company_id and company_id.pe_private_key or False
            values['pe_public_key'] = company_id and company_id.pe_public_key or False
            values['company_id'] = company_id and company_id.id or False
            
            #if company_id:
            #    invoice_journal_id = self.env['account.journal'].search([('company_id','=',company_id.id),
            #                                                             ('type','=','sale'),
            #                                                             ('pe_invoice_code','=','01')], limit=1)
            #    values['invoice_journal_id'] = invoice_journal_id.id or False
            #    voucher_journal_id = self.env['account.journal'].search([('company_id','=',company_id.id),
            #                                                             ('type','=','sale'),
            #                                                             ('pe_invoice_code','=','03')], limit=1)
                
            #    values['voucher_journal_id'] = voucher_journal_id.id or False
        return values
    
    
    def appy_configuration(self):
        self.ensure_one()
        values = {}
        values['pe_ws_type'] = self.pe_ws_type or False
        values['pe_ws_server'] = self.pe_ws_server or False
        values['pe_ws_url'] = self.pe_ws_url or False
        values['pe_ws_status_url'] = self.pe_ws_status_url or False
        values['pe_ws_user'] = self.pe_ws_user or False
        values['pe_ws_password'] = self.pe_ws_password or False
        values['pe_private_key'] = self.pe_private_key or False
        values['pe_public_key'] = self.pe_public_key or False
        self.company_id.write(values)
    