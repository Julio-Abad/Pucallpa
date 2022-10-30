# -*- coding: utf-8 -*-

from odoo.http import content_disposition, Controller, request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import _


class CustomerPortal(CustomerPortal):
    
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "pe_doc_type", "pe_doc_number"]
    
    def details_form_validate(self, data):
        error, error_message = super(CustomerPortal, self).details_form_validate(data)
        if data.get('pe_doc_type') and not data.get('pe_doc_number'):
            error["pe_doc_number"] = 'error'
            error_message.append(_('The document number is required.'))
        if not data.get('pe_doc_type') and data.get('pe_doc_number'):
            error["pe_doc_number"] = 'error'
            error_message.append(_('The document type is required.'))
        
        if data.get('pe_doc_type') in ['1','6'] and data.get('pe_doc_number'):
            if data.get('pe_doc_type') in ['1'] and (not data.get('pe_doc_number').isdigit() or len(data.get('pe_doc_number'))!=8):
                error["pe_doc_number"] = 'error'
                error_message.append(_('The DNI it is invalid.'))
            if data.get('pe_doc_type') in ['6'] and (not data.get('pe_doc_number').isdigit() or not request.env['res.partner'].validate_ruc(data.get('pe_doc_number'))):
                error["pe_doc_number"] = 'error'
                error_message.append(_('The RUC it is invalid.'))
        return error, error_message