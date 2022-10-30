# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountEdiDocument(models.Model):
    _inherit = [
        "account.edi.document",
        "pe.cpe.mixin",
    ]
    _name = "account.edi.document"

    #state = fields.Selection([('to_send', 'To Send'), ('sent', 'Sent'), ('to_cancel', 'To Cancel'), ('cancelled', 'Cancelled')])
    name = fields.Char(store = True)
    attachment_id = fields.Many2one(readonly=True, states={'to_send': [('readonly', False)]})
    move_id = fields.Many2one(readonly=True, states={'to_send': [('readonly', False)]})
    edi_format_id = fields.Many2one(readonly=True, states={'to_send': [('readonly', False)]})
    error = fields.Html(readonly=True, states={'to_send': [('readonly', False)]})
    
    def _process_documents_no_web_services(self):
        super(AccountEdiDocument, self)._process_documents_no_web_services()
        jobs = self.filtered(lambda d: d.edi_format_id.code == 'pe_cpe' )._prepare_jobs()
        self._process_jobs(self._convert_to_old_jobs_format(jobs))

    
    @api.model
    def _process_job(self, documents, doc_type):
        def _postprocess_post_edi_results(documents, edi_result):
            attachments_to_unlink = self.env['ir.attachment']
            for document in documents:
                move = document.move_id
                move_result = edi_result.get(move, {})
                if document.pe_send_date and move_result.get('pe_send_date'):
                    del move_result['pe_send_date']
                if move_result.get('attachment_id') and not move_result.get('error', False):
                    old_attachment = document.attachment_id
                    if move_result.get('pe_response_id'):
                        move_result.update({'state': 'sent'})
                    elif move_result.get('state','')=='sent':
                        move_result.update({'state': 'sent'})
                    else:
                        move_result.update({'state':'to_send'})
                    if move.company_id.pe_ws_server == 'nubefact_pse':
                        response = """ <ul>
                                        <li><a target="_blank" href="%s">Enlace</a></li>
                                        <li><a target="_blank" href="%s">PDF</a></li>
                                        <li><a target="_blank" href="%s">XML</a></li>
                                        <li><a target="_blank" href="%s">CDR</a></li>
                                    </ul>""" % (move_result.get('enlace'),
                                                move_result.get('enlace_del_pdf', "#"),
                                                move_result.get('enlace_del_xml', "#"),
                                                move_result.get('enlace_del_cdr', "#"))
                        move.message_post(body=_('Sending the electronic document succeeded.<br/>%s' % response))
                    if move_result.get('enlace'):
                        del move_result['enlace']
                    if move_result.get('enlace_del_pdf'):
                        del move_result['enlace_del_pdf']
                    if move_result.get('enlace_del_xml'):
                        del move_result['enlace_del_xml']
                    if move_result.get('enlace_del_cdr'):
                        del move_result['enlace_del_cdr']
                    document.write(move_result)
                    if not old_attachment.res_model or not old_attachment.res_id:
                        attachments_to_unlink |= old_attachment
                else:
                    document.write({
                        'error': move_result.get('error', False),
                        'state': 'to_cancel',
                        'blocking_level': move_result.get('blocking_level', "warning") if 'error' in move_result else False,
                    })
                    move.message_post(body=move_result.get('error', ''))

            # Attachments that are not explicitly linked to a business model could be removed because they are not
            # supposed to have any traceability from the user.
            attachments_to_unlink.unlink()

        def _postprocess_cancel_edi_results(documents, edi_result):
            invoice_ids_to_cancel = set()  # Avoid duplicates
            attachments_to_unlink = self.env['ir.attachment']
            for document in documents:
                move = document.move_id
                move_result = edi_result.get(move, {})
                if move_result.get('success') is True:
                    old_attachment = document.attachment_id
                    document.write({
                        'state': 'cancelled',
                        'error': False,
                        'blocking_level': False,
                    })

                    if move.is_invoice(include_receipts=True) and move.state == 'posted':
                        # The user requested a cancellation of the EDI and it has been approved. Then, the invoice
                        # can be safely cancelled.
                        invoice_ids_to_cancel.add(move.id)

                    #if not old_attachment.res_model or not old_attachment.res_id:
                    #    attachments_to_unlink |= old_attachment

                elif not move_result.get('success'):
                    document.write({
                        'error': move_result.get('error', False),
                        'blocking_level': move_result.get('blocking_level', "warning") if move_result.get('error') else False,
                    })

            if invoice_ids_to_cancel:
                invoices = self.with_context(pe_annul_document = True).env['account.move'].browse(list(invoice_ids_to_cancel))
                invoices.button_draft()
                invoices.button_cancel()
                invoices.write({'pe_annul':False})

            # Attachments that are not explicitly linked to a business model could be removed because they are not
            # supposed to have any traceability from the user.
            #attachments_to_unlink.unlink()

        if documents.filtered(lambda s: s.edi_format_id.code!='pe_cpe'):
            super(AccountEdiDocument, self)._process_job(documents.filtered(lambda s: s.edi_format_id.code!='pe_cpe'), 
                                                         doc_type)
        elif documents.filtered(lambda s: s.edi_format_id.code=='pe_cpe'):
            documents = documents.filtered(lambda s: s.edi_format_id.code=='pe_cpe')
            test_mode = self._context.get('edi_test_mode', False)
    
            documents.edi_format_id.ensure_one()  # All account.edi.document of a job should have the same edi_format_id
            documents.move_id.company_id.ensure_one()  # All account.edi.document of a job should be from the same company
            if len(set(doc.state for doc in documents)) != 1:
                raise ValueError('All account.edi.document of a job should have the same state')
    
            edi_format = documents.edi_format_id
            state = documents[0].state
            if doc_type == 'invoice':
                if state == 'to_send':
                    edi_result = edi_format._post_invoice_edi(documents.move_id, test_mode=test_mode)
                    _postprocess_post_edi_results(documents, edi_result)
                elif state == 'to_cancel':
                    edi_result = edi_format._cancel_invoice_edi(documents.move_id, test_mode=test_mode)
                    _postprocess_cancel_edi_results(documents, edi_result)
    
            elif doc_type == 'payment':
                if state == 'to_send':
                    edi_result = edi_format._post_payment_edi(documents.move_id, test_mode=test_mode)
                    _postprocess_post_edi_results(documents, edi_result)
                elif state == 'to_cancel':
                    edi_result = edi_format._cancel_payment_edi(documents.move_id, test_mode=test_mode)
                    _postprocess_cancel_edi_results(documents, edi_result)
            
        