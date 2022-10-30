# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from base64 import b64encode, decodestring, encodebytes
from datetime import datetime, timedelta
from odoo.exceptions import Warning, UserError, ValidationError
import requests
import zipfile
from io import BytesIO

class PeCpeMixin(models.AbstractModel):
    _name = 'pe.cpe.mixin'
    _description = "Sunat CPE"

    pe_date = fields.Date("Date", default=fields.Date.context_today, readonly=True, states={'to_send': [('readonly', False)]})
    pe_response_id = fields.Many2one("ir.attachment", "XML Response", readonly=True)
    
    pe_response = fields.Char("Response", readonly=True)
    pe_response_code = fields.Char("Response Code", readonly=True)
    
    pe_note = fields.Text("Note", readonly=True)
    
    pe_return_code = fields.Selection("_get_pe_return_code", string= "Return Code", readonly=True)
    
    pe_digest = fields.Char("Digest", readonly=True)
    
    pe_ticket = fields.Char("Ticket", readonly=True)
    pe_ticket_api = fields.Char("Api Ticket", readonly=True)
    
    pe_send_date_pe = fields.Datetime("Send Date UTC-5", readonly=True, states={'to_send': [('readonly', False)]})
    pe_date_end = fields.Datetime("End Date", readonly=True, states={'to_send': [('readonly', False)]})
    pe_send_date = fields.Datetime("Send Date", readonly=True, states={'to_send': [('readonly', False)]})
    pe_branch_code = fields.Char("Branch Code", readonly=True, states={'to_send': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    
    #def unlink(self):
    #    for cpe in self:
    #        if cpe.name!="/" and cpe.state !="draft":
    #            raise Warning(_('You can only delete sent documents.'))
    #    return super(PeCpe, self).unlink()
    
    def _pe_cpe_document_name(self, document_id=False):
        if self._name == 'account.edi.document':
            document_id = self.move_id
        elif self._name == 'pe.eguide':
            document_id = self.picking_id
        if document_id and document_id._name in ['account.move', 'stock.picking']:
            if document_id._name == 'account.move':
                ruc= document_id.company_id.partner_id.pe_doc_number
                doc_code= "-%s" % document_id.pe_invoice_code
                number = document_id.name
            elif document_id._name == 'stock.picking':
                ruc= document_id.company_id.partner_id.pe_doc_number
                doc_code= "-%s" % '09'
                number = document_id.pe_guide_number
        else:
            ruc= self.company_id.partner_id.pe_doc_number
            doc_code= ""
            number = self.name or ""
        return "%s%s-%s" %(ruc, doc_code, number)
    
    @api.model
    def _get_pe_return_code(self):
        return self.env['pe.catalog.return'].get_selection()
    
    def action_to_send(self):
        self.write({'state':'to_send'})
    
    def action_generate(self):
        for cpe in self:
            if not cpe.pe_send_date:
                record = cpe.with_context(tz = "America/Lima")
                date = datetime.now()
                send_date = fields.Datetime.context_timestamp(record, date)
                if (send_date.date() - cpe.pe_date).days > 7:
                    send_date = cpe.pe_date + timedelta(days=6)
                cpe.pe_send_date = fields.Datetime.to_string(send_date)
    
    def _pe_check_nubefact_pse_response(self, response, xml_name):
        vals = {}
        if not response:
            return vals
        if response.get('errors', False):
            vals['error'] = response.get('errors', False)
            vals['pe_response'] = response.get('errors', False)
        if response.get('enlace', False):
            vals['enlace'] = response.get('enlace', False)
        if response.get('enlace_del_pdf', False):
            vals['enlace_del_pdf'] = response.get('enlace_del_pdf', False)
        if response.get('enlace_del_xml', False):
            vals['enlace_del_xml'] = response.get('enlace_del_xml', False)
        if response.get('enlace_del_cdr', False):
            vals['enlace_del_cdr'] = response.get('enlace_del_cdr', False)
        if response.get('enlace_del_xml', False):
            try:
                res = requests.get(response.get('enlace_del_xml', False))
                attachment_id = self.env['ir.attachment'].create({
                        'name': "%s.xml" % xml_name,
                        'datas': encodebytes(res.content),
                        'mimetype': 'application/xml'
                    })
                vals['attachment_id'] = attachment_id.id
                
            except Exception:
                attachment_id = self.env['ir.attachment'].create({
                        'name': "%s.xml" % xml_name,
                        'url': response.get('enlace_del_xml', False),
                        'type': 'url',
                        'mimetype': 'application/xml'
                    })
                vals['attachment_id'] = attachment_id.id
        if response.get('enlace_del_cdr', False):
            try:
                res = requests.get(response.get('enlace_del_cdr', False))
                zip_data = BytesIO()
                zip_file = zipfile.ZipFile(zip_data, "w", zipfile.ZIP_DEFLATED, False)
                zip_file.writestr("R-%s.xml" % xml_name, res.content)
                zip_file.close()
                pe_response_id = self.env['ir.attachment'].create({
                                                     'name': "R-%s.zip" % xml_name,
                                                     'datas': b64encode(zip_data.getvalue()),
                                                     'mimetype': 'application/zip'
                                                 })
                vals['pe_response_id'] = pe_response_id.id
            except Exception:
                pe_response_id = self.env['ir.attachment'].create({
                                                     'name': "R-%s.xml" % xml_name,
                                                     'url': response.get('enlace_del_cdr'),
                                                     'type': 'url',
                                                     'mimetype': 'application/xml'
                                                })
                vals['pe_response_id'] = pe_response_id.id
        if response.get('sunat_description', False):
            vals['pe_response'] = response.get('sunat_description', False)
        pe_note = ""
        if response.get('sunat_note', ''):
            pe_note+= response.get('sunat_note', '')
        if response.get('sunat_soap_error', False):
            pe_note+= "\n%s" % response.get('sunat_soap_error', '')
        vals['pe_note'] = pe_note
        if response.get('sunat_responsecode') and not vals.get('pe_return_code'):
            res_code ="%04d" % int(response.get('sunat_responsecode'))
            if self.env['pe.catalog.return'].get_by_code(res_code):
                vals['pe_return_code'] = res_code    
        if response.get('enlace', False) or response.get('enlace_del_cdr', False):
            vals['state'] = 'sent'
        vals['pe_digest'] = response.get('codigo_hash', False)
        return vals
    
    
    def action_sent(self):
        for cpe in self:
            if cpe._name == 'account.edi.document':
                if cpe.edi_format_id.code == 'pe_cpe':
                    cpe._process_documents_web_services(with_commit=False)
            else:
                type = cpe._name == 'pe.cpe.rc' and 'rc' or 'ra'
                data = self.env['pe.cpe.send'].send_document(cpe, type, cpe.attachment_id.datas)
                if cpe.company_id.pe_ws_server in ['nubefact_pse']:
                    document_name = cpe._pe_cpe_document_name()
                    vals = cpe._pe_check_nubefact_pse_response(data.get('datos_respuesta', False) or data.get('respuesta'), document_name)
                    for move in cpe.voided_ids:
                        if vals.get('enlace'):
                            if move.company_id.pe_ws_server == 'nubefact_pse':
                                response = """ <ul>
                                                <li><a target="_blank" href="%s">Enlace</a></li>
                                                <li><a target="_blank" href="%s">PDF</a></li>
                                                <li><a target="_blank" href="%s">XML</a></li>
                                                <li><a target="_blank" href="%s">CDR</a></li>
                                            </ul>""" % (vals.get('enlace'),
                                                        vals.get('enlace_del_pdf', "#"),
                                                        vals.get('enlace_del_xml', "#"),
                                                        vals.get('enlace_del_cdr', "#"))
                                move.message_post(body=_('Sending the voided electronic document succeeded.<br/>%s' % response))
                    if vals.get('error'):
                        del vals['error']
                    if vals.get('enlace'):
                        del vals['enlace']
                    if vals.get('enlace_del_pdf'):
                        del vals['enlace_del_pdf']
                    if vals.get('enlace_del_xml'):
                        del vals['enlace_del_xml']
                    if vals.get('enlace_del_cdr'):
                        del vals['enlace_del_cdr']
                    cpe.write(vals)
                else:
                    cpe.pe_ticket = data.get('datos_respuesta', False) or False
                    if not cpe.pe_ticket:
                        cpe._check_pe_cpe_response(data.get('respuesta'))
                    if cpe.pe_ticket:
                        cpe.state = 'to_check'
        
    
    def _check_pe_cpe_response(self, response):
        self.ensure_one()
        if response.get('codigo'):
            if self.env['pe.catalog.return'].get_by_code(response.get('codigo')):
                self.pe_return_code = response.get('codigo')
        if response.get('respuesta'):
            self.pe_response = response.get('respuesta')
        if response.get('codigo') == '0000':
            self.state = 'sent'
            date_end = fields.Datetime.to_string(fields.Datetime.now())
            self.pe_date_end = date_end
            if self._name == 'pe.cpe.rc':
                edi_document_ids = self.summary_ids.filtered(lambda s: s.pe_condition_code not in ['3']).mapped('edi_document_ids').filtered(lambda s: s.edi_format_id.code == 'pe_cpe')
                if edi_document_ids:
                    edi_document_ids.write({'state':'sent',
                                            'pe_return_code': self.pe_return_code,
                                            'pe_date_end': date_end, 
                                            'pe_response': self.pe_response})
                edi_document_ids = self.summary_ids.filtered(lambda s: s.pe_condition_code in ['3']).mapped('edi_document_ids').filtered(lambda s: s.edi_format_id.code == 'pe_cpe')
                if edi_document_ids:
                    edi_document_ids.write({'state':'cancelled',
                                            'pe_return_code': self.pe_return_code,
                                            'pe_date_end': date_end, 
                                            'pe_response': self.pe_response})
                move_ids = self.summary_ids.filtered(lambda s: s.pe_annul==True and s.pe_condition_code not in ['3'])
                if move_ids:
                    summary_id = self.create({'pe_date':self.pe_date, 'company_id':self.company_id.id})
                    move_ids.write({'pe_summary_id':summary_id.id, 'pe_condition_code':'3'})
            #if self._name == 'pe.cpe.ra':
                #edi_document_ids = self.voided_ids.mapped('edi_document_ids').filtered(lambda s: s.edi_format_id.code == 'pe_cpe')
                #edi_document_ids.write('')
        if response.get('nota'):
            self.pe_note = response.get('nota')
        res = ""
        if response.get('faultcode'):
            code = response.get('faultcode', '').split(".")[-1]
            if self.env['pe.catalog.return'].get_by_code(code):
                self.pe_return_code = code
            self.pe_response = response.get('faultcode')
            res = "%s "  % response.get('faultcode')
        if response.get('faultstring'):
            res += response.get('faultstring', "")
        if res:
            self.pe_note = res
    
    def action_done(self):
        for cpe in self:
            if cpe._name in ['pe.cpe.rc', 'pe.cpe.ra']:
                data = self.env['pe.cpe.send'].get_document_status(cpe, 'ticket')
                if data.get('datos_respuesta'):
                    document_name = "R-%s.zip" % cpe._pe_cpe_document_name()
                    pe_response_id = self.env['ir.attachment'].create({
                                         'name': document_name,
                                         'datas': data.get('datos_respuesta'),
                                         'mimetype': 'application/zip'
                                     })
                    cpe.pe_response_id = pe_response_id
                if data.get('estado') and data.get('datos_respuesta'):
                    self._check_pe_cpe_response(data.get('respuesta'))
                
                #if cpe.state == 'sent' and cpe._name == 'pe.cpe.rc':
                #    if  cpe.is_voided==False:
                #        for invoice_id in self.summary_ids.filtered(lambda inv: inv.state in ['annul']):
                #            pe_summary_id=self.get_cpe_async("rc", invoice_id.id, True)
                #            invoice_id.pe_summary_id=pe_summary_id.id
        return True
    
    def _get_branch(self, invoice_id):
        return {'pe_branch_code':invoice_id.company_id.pe_branch_code or '0000'}

    @api.model
    def get_cpe_async(self, inv_id):
        res=None
        invoice_id = self.env['account.move'].browse([inv_id])
        company_id= invoice_id.company_id.id
        date_invoice= invoice_id.invoice_date
        pe_branch = self._get_branch(invoice_id)
        querry = [('state', '=', 'to_send'), ('pe_date', '=', date_invoice), ('name', '=', "/"), 
                  ('company_id', '=', company_id),('pe_branch_code','=',pe_branch.get('pe_branch_code'))]
        if self._name == 'pe.cpe.rc':
            querry.append(('pe_invoice_code','=', invoice_id.pe_invoice_code))
        cpe_ids=self.search(querry, order="pe_date DESC")
        for cpe_id in cpe_ids:
            if self._name == 'pe.cpe.rc':
                if cpe_id and len(cpe_id.summary_ids.ids)<499:
                    res=cpe_id
                    break
            else:
                if cpe_id and len(cpe_id.voided_ids.ids)<499:
                    res=cpe_id
                    break
        if not res:
            vals={}
            vals['pe_date'] = date_invoice
            vals['company_id']= company_id
            vals['pe_branch_code'] = pe_branch.get('pe_branch_code')
            if self._name == 'pe.cpe.rc':
                vals['pe_invoice_code'] = invoice_id.pe_invoice_code
            if pe_branch.get('branch_id'):
                vals['branch_id'] = pe_branch.get('branch_id')
            res=self.create(vals)
        return res
    
    def get_pe_document_name(self):
        self.ensure_one()
        ruc= self.company_id.partner_id.pe_doc_number
        if self._name == 'account.edi.document':
            doc_code= "-%s" % self.move_id.pe_invoice_code
            number = self.move_id.name
        else:
            doc_code= ""
            number = self.name or ""
        return "%s%s-%s" %(ruc, doc_code, number)

    def action_document_status(self):
        for cpe in self:
            if cpe._name in ['pe.cpe.rc', 'pe.cpe.ra']:
                data = self.env['pe.cpe.send'].with_context(document_status=True).get_document_status(cpe, 'ticket')
                if cpe.company_id.pe_ws_server in ['nubefact_pse']:
                    xml_name = cpe.get_pe_document_name()
                    move_result = cpe._pe_check_nubefact_pse_response(data.get('respuesta'), xml_name)
                    if move_result.get('error'):
                        del move_result['error']
                    if move_result.get('enlace'):
                        del move_result['enlace']
                    if move_result.get('enlace_del_pdf'):
                        del move_result['enlace_del_pdf']
                    if move_result.get('enlace_del_xml'):
                        del move_result['enlace_del_xml']
                    if move_result.get('enlace_del_cdr'):
                        del move_result['enlace_del_cdr']
                    cpe.write(move_result)
                else:
                    if data.get('datos_respuesta'):
                        document_name = "R-%s.zip" % cpe._pe_cpe_document_name()
                        pe_response_id = self.env['ir.attachment'].create({
                                             'name': "R-%s.zip" % document_name,
                                             'datas': data.get('datos_respuesta'),
                                             'mimetype': 'application/zip'
                                         })
                        cpe.pe_response_id = pe_response_id
                    if data.get('estado') and data.get('respuesta'):
                        self._check_pe_cpe_response(data.get('respuesta'))
                    
                #if cpe.state == 'done' and cpe.type == 'rc':
                #    if  cpe.is_voided==False:
                #        for invoice_id in self.summary_ids.filtered(lambda inv: inv.state in ['annul']):
                #            pe_summary_id=self.get_cpe_async("rc", invoice_id.id, True)
                #            invoice_id.pe_summary_id=pe_summary_id.id
            else:
                data = self.env['pe.cpe.send'].with_context(document_status=True).get_document_status(cpe, 'status')
                if data.get('estado') and data.get('respuesta'):
                    xml_name = cpe._pe_cpe_document_name()
                    if cpe.company_id.pe_ws_server in ['nubefact_pse']:
                        move_result = cpe._pe_check_nubefact_pse_response(data.get('respuesta'), xml_name)
                        if move_result.get('enlace'):
                            del move_result['enlace']
                        if move_result.get('enlace_del_pdf'):
                            del move_result['enlace_del_pdf']
                        if move_result.get('enlace_del_xml'):
                            del move_result['enlace_del_xml']
                        if move_result.get('enlace_del_cdr'):
                            del move_result['enlace_del_cdr']
                        if cpe._name=='pe.eguide':
                            if move_result.get('error'):
                                del move_result['error']
                        cpe.write(move_result)
                    else:
                        cpe._check_pe_cpe_response(data.get('respuesta'))
                        if data.get('datos_respuesta'):
                            pe_response_id = self.env['ir.attachment'].create({
                                                 'name': "R-%s.zip" % xml_name,
                                                 'datas': data.get('datos_respuesta'),
                                                 'mimetype': 'application/zip'
                                             })
                            cpe.pe_response_id = pe_response_id.id

    def pe_send_all(self):
        cpe_ids = self.search([('state', 'in', ['to_send', 'generate', 'to_check']), ('pe_ticket','=',False)], limit = 100)
        for cpe_id in cpe_ids:
            try:
                if cpe_id.pe_ticket:
                    cpe_id.action_done()
                else:
                    cpe_id.action_generate()
                    cpe_id.action_sent()
            except Exception:
                pass
    

    def pe_check_ticket(self):
        cpe_ids = self.search([('pe_ticket', '!=', False),('state','not in',['to_cancel','cancelled'])])
        for cpe_id in cpe_ids:
            try:
                if cpe_id.pe_ticket:
                    cpe_id.action_done()
            except Exception:
                pass
    
    
    def pe_send_async_cpe(self):
        cpe_ids = self.search([('state', 'in', ['to_send']),('move_id.pe_invoice_code','!=','03'),('edi_format_id.code','=','pe_cpe')])
        for cpe_id in cpe_ids:
            if cpe_id.move_id:
                if cpe_id.move_id.pe_invoice_code not in ["03"] and (cpe_id.move_id.reversed_entry_id.pe_invoice_code not in ["03"] or 
                                                                     cpe_id.move_id.debit_origin_id.pe_invoice_code not in ["03"]):
                    try:
                        cpe_id.action_document_status()
                    except Exception:
                        pass
                if cpe_id.state != 'done':
                    if cpe_id.move_id.pe_invoice_code not in ["03"] and (cpe_id.move_id.reversed_entry_id.pe_invoice_code not in ["03"] or 
                                                                     cpe_id.move_id.debit_origin_id.pe_invoice_code not in ["03"]):
                        try:
                            cpe_id.action_generate()
                            cpe_id.action_sent()
                        except Exception:
                            pass
                
    def get_pe_sequence_id(self, prefix):
        self.ensure_one()
        sequence_id = self.env['ir.sequence'].search([('code','=', self._name),('company_id','=',self.company_id.id)], limit = 1)
        if not sequence_id:
            sequence_id = self.set_pe_sequence_id(prefix)
        else:
            if sequence_id.prefix != prefix:
               sequence_id.prefix = prefix 
            #date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', sequence_id.id), ('date_from', '>=', self.start_date), ('date_from', '<=', self.end_date)], order='date_from desc', limit=1)
            #date_range.number_next_actual = 1
        return sequence_id
    
    def set_pe_sequence_id(self, prefix):
        self.ensure_one()
        vals = {}
        vals['name'] = _("Sequence %s") % self._name
        vals['code'] = self._name
        vals['company_id'] = self.company_id.id
        vals['use_date_range'] = False
        #vals['range_reset'] = 'monthly'
        vals['prefix'] = prefix
        sequence_id = self.env['ir.sequence'].sudo().create(vals)
        return sequence_id
    
    def action_to_cancel(self):
        self.write({'state':'to_cancel'})
    
    def action_cancelled(self):
        self.write({'state':'cancelled'})
    
        
class PeCpeRC(models.Model):
    _inherit = [
        "pe.cpe.mixin",
    ]
    _name = "pe.cpe.rc"    
    _description = "Daily Summary"
    
    name = fields.Char("Name", default="/", readonly=True, states={'to_send': [('readonly', False)]})
    state = fields.Selection([('to_send', 'To Send'), ('generate','Generate'), ('to_check','To Check'), 
                              ('sent', 'Sent'), ('to_cancel', 'To Cancel'), ('cancelled', 'Cancelled')], default='to_send')
    attachment_id = fields.Many2one('ir.attachment', help='The file generated by edi_format_id when the invoice is posted (and this document is processed).', 
                                    readonly=True, states={'to_send': [('readonly', False)]})
    summary_ids = fields.One2many("account.move", "pe_summary_id", string="Summary Invoices")
    pe_invoice_code = fields.Selection(selection="_get_pe_invoice_code", string="Invoice Type Code", 
                                       readonly=True, states={'to_send': [('readonly', False)]})
    
    _order = 'pe_date desc, pe_invoice_code asc, name desc, id desc'
    
    
    @api.model
    def _get_pe_invoice_code(self):
        return self.env['pe.catalog.01'].get_selection()
    
    def action_generate(self):
        super(PeCpeRC, self).action_generate()
        for cpe in self:
            cpe.state = 'generate'
            if cpe.name=='/':
                local_date =cpe.pe_send_date.date()
                cpe.name= cpe.get_pe_sequence_id("RC-%(year)s%(month)s%(day)s-").with_context(ir_sequence_date=local_date).next_by_id(local_date) # self.env['ir.sequence'].with_context(ir_sequence_date=local_date).next_by_code('pe.sunat.cpe.ra') 
            elif "RC-%s" % cpe.pe_send_date.strftime("%Y%m%d") not in cpe.name:
                local_date =cpe.pe_send_date.date()
                cpe.name= cpe.get_pe_sequence_id("RC-%(year)s%(month)s%(day)s-").with_context(ir_sequence_date=local_date).next_by_id(local_date)
            file_name = cpe.get_pe_document_name()
            data = self.env['pe.cpe.send'].get_document(cpe)
            cpe.pe_digest = data.get('resumen', False)
            xml_content = data.get('xml_firmado')
            attachment_id = self.env['ir.attachment'].create({
                'name': "%s.xml" % file_name,
                'datas': xml_content,
                'mimetype': 'application/xml'
            })
            self.attachment_id = attachment_id
    
    def action_sent(self):
        super(PeCpeRC, self).action_sent()
        self.filtered(lambda cpe: cpe.state not in ['sent', 'to_check']).write({'state':'generate'})
    
    def unlink(self):
        cpe_ids = self.filtered(lambda s:s.state!='to_send')
        if cpe_ids:
            raise ValidationError("No Puede Eliminar un Documento Enviado a la SUNAT")
        return super(PeCpeRC, self).unlink()
    
class PeCpeRA(models.Model):
    _inherit = [
        "pe.cpe.mixin",
    ]
    _name = "pe.cpe.ra"    
    _description = "Low communication"
    
    name = fields.Char("Name", default="/", readonly=True, states={'to_send': [('readonly', False)]})
    state = fields.Selection([('to_send', 'To Send'), ('generate','Generate'), ('to_check','To Check'), 
                              ('sent', 'Sent'), ('to_cancel', 'To Cancel'), ('cancelled', 'Cancelled')], default='to_send')
    attachment_id = fields.Many2one('ir.attachment', help='The file generated by edi_format_id when the invoice is posted (and this document is processed).', 
                                    readonly=True, states={'to_send': [('readonly', False)]})
    voided_ids = fields.One2many("account.move", "pe_voided_id", string="Voided Invoices")
    
    def action_generate(self):
        super(PeCpeRA, self).action_generate()
        for cpe in self:
            cpe.state = 'generate'
            if cpe.name=='/':
                local_date =cpe.pe_send_date.date()
                cpe.name= cpe.get_pe_sequence_id("RA-%(year)s%(month)s%(day)s-").with_context(ir_sequence_date=local_date).next_by_id(local_date) # self.env['ir.sequence'].with_context(ir_sequence_date=local_date).next_by_code('pe.sunat.cpe.ra') 
            elif "RA-%s" % cpe.pe_send_date.strftime("%Y%m%d") not in cpe.name:
                local_date =cpe.pe_send_date.date()
                cpe.name= cpe.get_pe_sequence_id("RA-%(year)s%(month)s%(day)s-").with_context(ir_sequence_date=local_date).next_by_id(local_date)
            if cpe.company_id.pe_ws_server in ['sunat']:
                file_name = cpe.get_pe_document_name()
                data = self.env['pe.cpe.send'].get_document(cpe)
                cpe.pe_digest = data.get('resumen', False)
                xml_content = data.get('xml_firmado')
                attachment_id = self.env['ir.attachment'].create({
                    'name': "%s.xml" % file_name,
                    'datas': xml_content,
                    'mimetype': 'application/xml'
                })
                self.attachment_id = attachment_id
    
    def action_sent(self):
        super(PeCpeRA, self).action_sent()
        self.filtered(lambda cpe: cpe.state not in ['sent', 'to_check']).write({'state':'generate'})
