# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
from odoo.exceptions import UserError
import base64
import re
from datetime import datetime
from librecpe.cpe import Cliente
import requests

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _needs_web_services(self):
        self.ensure_one()
        return True if self.code == 'pe_cpe' else super()._needs_web_services()
    
    def _is_compatible_with_journal(self, journal):
        self.ensure_one()
        res = super()._is_compatible_with_journal(journal)
        if self.code != 'pe_cpe':
            return res
        return journal.type == 'sale'
    
    def _is_embedding_to_invoice_pdf_needed(self):
        self.ensure_one()
        return True if self.code == 'pe_cpe' else super()._is_embedding_to_invoice_pdf_needed()
    
    def _post_invoice_edi(self, invoices, test_mode=False):
        self.ensure_one()
        if self.code != 'pe_cpe':
            return super()._post_invoice_edi(invoices, test_mode=test_mode)
        res = {}
        for invoice in invoices:
            vals = self._export_pe_cpe(invoice)
            res[invoice] = vals
        return res
    
    def _cancel_invoice_edi(self, invoices, test_mode=False):
        # self.ensure_one()
        # if self.code != 'pe_cpe':
        return super(AccountEdiFormat, self)._cancel_invoice_edi(invoices, test_mode)
        #for invoice in invoices:
        #    if not invoice.pe_voided_id:
        #        invoice._button_pe_annul()
        # pe_voided_ids = invoices.mapped('pe_voided_id')
        # pe_voided_ids.filtered(lambda s: s.state in ['to_send']).action_generate()
        # invoice_ids = pe_voided_ids.mapped('voided_ids')
        # try:
        #     pe_voided_ids.filtered(lambda s: s.state in ['generate']).action_sent()
        #
        # except Exception:
        #     pass
        # try:
        #     pe_voided_ids.filtered(lambda s: s.state in ['to_check'] and s.pe_ticket).action_done()
        # except Exception:
        #     pass
        # vals = {}
        # for invoice in invoices:
        #     if invoice.pe_voided_id.state == 'sent':
        #         vals[invoice]= {'success': True}
        #     else:
        #         vals[invoice]= {'blocking_level': 'info',
        #                           'error':invoice.pe_voided_id.pe_response}
        # return vals
    
    def _pe_check_response(self, response):
        self.ensure_one()
        vals = {}
        if response.get('codigo'):
            if self.env['pe.catalog.return'].get_by_code(response.get('codigo')):
                vals['pe_return_code'] = response.get('codigo')
        if response.get('respuesta'):
            vals['pe_response'] = response.get('respuesta')
        if response.get('nota'):
            vals['pe_note'] = response.get('nota')
        res = ""
        if response.get('faultcode'):
            code = response.get('faultcode', '').split(".")[-1]
            if self.env['pe.catalog.return'].get_by_code(code):
                vals['pe_return_code'] = code
            vals['pe_response'] = response.get('faultcode')
            res = "%s "  % response.get('faultcode')
        if response.get('faultstring'):
            res += response.get('faultstring', "")
        if res:
            vals['pe_note'] = str(res)
        return vals
    
    # def _pe_check_nubefact_pse_response(self, response, xml_name):
    #     vals = {}
    #     if not response:
    #         return vals
    #     if response.get('errors', False):
    #         vals['error'] = response.get('errors', False)
    #     if response.get('enlace', False):
    #         vals['enlace'] = response.get('enlace', False)
    #     if response.get('enlace_del_pdf', False):
    #         vals['enlace_del_pdf'] = response.get('enlace_del_pdf', False)
    #     if response.get('enlace_del_xml', False):
    #         vals['enlace_del_xml'] = response.get('enlace_del_xml', False)
    #     if response.get('enlace_del_cdr', False):
    #         vals['enlace_del_cdr'] = response.get('enlace_del_cdr', False)
    #     if response.get('enlace_del_xml', False):
    #         attachment_id = self.env['ir.attachment'].create({
    #                 'name': "%s.xml" % xml_name,
    #                 'url': response.get('enlace_del_xml', False),
    #                 'type': 'url',
    #                 'mimetype': 'application/xml'
    #             })
    #         vals['attachment_id'] = attachment_id.id
    #     if response.get('enlace_del_cdr', False):
    #         pe_response_id = self.env['ir.attachment'].create({
    #                                              'name': "R-%s.xml" % xml_name,
    #                                              'url': response.get('enlace_del_cdr'),
    #                                              'type': 'url',
    #                                              'mimetype': 'application/xml'
    #                                          })
    #         # try:
    #         #     xml = requests.get(response.get('enlace_del_cdr'))
    #         #     if xml.status_code == 200:
    #         #         vals.update(self._pe_check_response(Cliente.obtenerRespuestaXML(xml.text.encode('utf-8')))) 
    #         # except Exception:
    #         #     pass
    #         vals['pe_response_id'] = pe_response_id.id
    #     vals['pe_response'] = response.get('sunat_description', False)
    #     pe_note = response.get('sunat_note', '')
    #     if response.get('sunat_soap_error', False):
    #         pe_note+= "\n%s" % response.get('sunat_soap_error', '')
    #     vals['pe_note'] = pe_note
    #     if response.get('sunat_responsecode') and not vals.get('pe_return_code'):
    #         res_code ="%04d" % int(response.get('sunat_responsecode'))
    #         if self.env['pe.catalog.return'].get_by_code(res_code):
    #             vals['pe_return_code'] = res_code    
    #     vals['pe_digest'] = response.get('codigo_hash', False)
    #     return vals
        
    
    def _export_pe_cpe(self, move_id):
        vals = {}
        if move_id.company_id.pe_ws_server in ['sunat']:
            data = self.env['pe.cpe.send'].get_document(move_id)
            xml_name =  move_id._pe_cpe_document_name(move_id)
            vals['pe_send_date'] = fields.Datetime.now()
            if move_id.company_id.pe_is_sync or move_id.journal_id.pe_is_synchronous:
                if move_id.pe_invoice_code in ['01'] or \
                   move_id.journal_id.pe_is_synchronous or \
                   move_id.reversed_entry_id.pe_invoice_code in ['01'] or \
                   move_id.debit_origin_id.pe_invoice_code in ['01']:
                    try:
                        send_data = self.env['pe.cpe.send'].send_document(move_id, 'sync', data.get('xml_firmado'))
                        if send_data.get('datos_respuesta'):
                            pe_response_id = self.env['ir.attachment'].create({
                                                 'name': "R-%s.zip" % xml_name,
                                                 'datas': send_data.get('datos_respuesta'),
                                                 'mimetype': 'application/zip'
                                             })
                            vals['pe_response_id'] = pe_response_id.id
                        vals.update(self._pe_check_response(send_data.get('respuesta', {})))
                        vals['pe_date_end'] = fields.Datetime.now()
                    except Exception:
                        pass
                else:
                    pe_summary_id=self.env['pe.cpe.rc'].get_cpe_async(move_id.id)
                    move_id.pe_summary_id=pe_summary_id.id   
            xml_content = data.get('xml_firmado')
            attachment_id = self.env['ir.attachment'].create({
                'name': "%s.xml" % xml_name,
                'datas': xml_content,
                'mimetype': 'application/xml'
            })
            vals['pe_digest'] = data.get('resumen', False)
            vals['attachment_id'] = attachment_id.id
        elif move_id.company_id.pe_ws_server in ['nubefact_pse']:
            send_data = self.env['pe.cpe.send'].send_document(move_id, 'sync')
            xml_name =  move_id._pe_cpe_document_name(move_id)
            vals.update(self.env['pe.cpe.mixin']._pe_check_nubefact_pse_response(send_data.get('respuesta', {}), xml_name))
        return vals
    
    def _check_move_configuration(self, move):
        self.ensure_one()
        if self.code != 'pe_cpe':
            return super(AccountEdiFormat, self)._check_move_configuration(move)
        res = []
        company_id = move.company_id
        if not company_id.pe_ws_type:
            res.append(_("The type of server is required"))
        if not company_id.pe_ws_server:
            res.append(_("The server is required"))
        if not company_id.pe_ws_url:
            res.append(_("The url of server is required"))
        if not company_id.pe_ws_status_url and company_id.pe_ws_server in ['sunat']:
            res.append(_("The url status of server is required"))
        if not company_id.pe_ws_user and company_id.pe_ws_server in ['sunat']:
            res.append(_("The user of server is required"))
        if not company_id.pe_ws_password:
            res.append(_("The password of server is required"))
        if not company_id.pe_private_key and company_id.pe_ws_server in ['sunat']:
            res.append(_("The private key is required"))
        if not company_id.pe_public_key and company_id.pe_ws_server in ['sunat']:
            res.append(_("The public key is required"))
        
        if move.journal_id.pe_invoice_code not in ['01', '03', '07', '08']:
            res.append("Documento no soportado, solo es posible emitir Facturas, Boletas, Notas de Credito y Debito")
        if move.move_type == 'out_invoice' and move.pe_invoice_code in ['07']:
            res.append("El tipo de documento no puede ser 07, Nota de Credito.")
        if move.move_type == 'out_refund' and move.pe_invoice_code not in ['07']:
            res.append("El tipo de documento debe ser 07, Nota de Credito.")
        if (move.pe_operation_type and move.pe_operation_type[:2]=="02"):
            for line in move.invoice_line_ids:
                if line.pe_type_affectation!="40":
                    res.append("El tipo de afectacion del producto %s debe ser Exportacion" %line.name)
        for line in move.invoice_line_ids:
            if line.display_type and line.display_type == 'line_section':
                continue
            if not line.product_id:
                res.append("Debe definir el producto %s " %line.name)
            if not line.product_id.default_code:
                res.append("El producto %s no tiene codigo" %line.name)
            if line.quantity==0.0 or line.price_unit == 0.0:
                res.append("La cantidad o precio del producto %s debe ser mayor a 0.0" %line.name)
            if not line.tax_ids and line.quantity>0:
                res.append("Es Necesario definir por lo menos un impuesto para el pruducto %s" %line.name)
            if line.product_id.pe_require_plate and not (line.pe_license_plate):
                res.append("Es Necesario registrar el numero de placa para el pruducto %s" %line.name)
            if not line.pe_type_affectation:
                res.append("Es Necesario el tipo de afectacion para el pruducto %s" %line.name)
        if not re.match(r'^(B|F){1}[A-Z0-9]{3}\-\d+$', move.name):
            res.append("El numero de la factura ingresada no cumple con el estandar.\n"\
                            "Verificar la secuencia del Diario por ejemplo F001- o BN01-. \n"\
                            "Para cambiar ir a Configuracion/Contabilidad/Diarios/Secuencia del asiento")
        
        if move.pe_invoice_code in ['03'] or move.reversed_entry_id.pe_invoice_code in ['03'] or move.debit_origin_id.pe_invoice_code in ['03']:
            doc_type = move.partner_id.pe_doc_type or '-'
            doc_number = move.partner_id.pe_doc_number or '-'
            if doc_type == '6' and doc_number[:2]!='10':
                res.append("El dato ingresado no cumple con el estandar \nTipo: %s \nNumero de documento: %s\n"\
                                "Deberia emitir una Factura. Cambiar en Factura/Otra Informacion/Diario"%(doc_type, doc_number))
            amount = company_id.pe_max_amount or 0
            if move.amount_total > amount and (doc_type=='-' or doc_number=='-'):
                res.append("El dato ingresado no cumple con el estandar \nTipo: %s \nNumero de documento: %s\nSon obligatorios el Tipo de Doc. y Numero"%(doc_type, doc_number))
        if move.pe_invoice_code in ['01'] or move.reversed_entry_id.pe_invoice_code in ['01'] or move.debit_origin_id.pe_invoice_code in ['01']:
            doc_type = move.partner_id.pe_doc_type or move.partner_id.parent_id.pe_doc_type or '-'
            doc_number = move.partner_id.pe_doc_number or move.partner_id.parent_id.pe_doc_number or '-'
            if doc_type not in ["0", '6'] or not doc_number:
                res.append(" El numero de documento de identidad del receptor debe ser RUC \nTipo: %s \nNumero de documento: %s"%(doc_type, doc_number))
        invoice_date = move.pe_invoice_date.date()
        today = fields.Datetime.context_timestamp(self, datetime.now())
        days = today.date() - invoice_date
        if days.days>move.company_id.pe_max_days and (move.pe_invoice_code in ['01'] or move.reversed_entry_id.pe_invoice_code in ['01']):
            res.append("La fecha de emision no puede ser menor a %d dias de hoy ni mayor a la fecha de hoy." % move.company_id.pe_max_days)
        if days.days<0:
            res.append("La fecha de emision no puede ser menor a %d dias de hoy ni mayor a la fecha de hoy." % move.company_id.pe_max_days)
        if move.pe_subject_detraction and not move.company_id.pe_detraction_account_number:
            res.append("Debe registrar la cuenta de Detracciones en Compañias")
        return res
            
        