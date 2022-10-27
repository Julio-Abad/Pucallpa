# Copyright 2019 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import http, _
from odoo.http import request

from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteForm(WebsiteForm):
    
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        res = super(WebsiteForm, self).website_form(model_name, **kwargs)
        values = {}
        if model_name == 'pe.query.cpe.form':
            values = json.loads(res.data)
            invoice_id = values and request.env[model_name].browse([values.get('id')]).invoice_id or False
            if invoice_id:
                url = invoice_id.sudo().get_portal_url()
                #values['url'] = url
                #return request.redirect(url)
            #elif invoice_id:
            #    values['error_fields'] = _("Document not found")
            return values and json.dumps(values) or res
        else:
            return res
    
    @http.route('/querycpe_response/', type='http', auth="public", methods=['POST','GET'], website=True)
    def querycpe_response(self, **kwargs):
        values = {}
        return json.dumps(values)
    
    def extract_data(self, model, values):
        """ Inject ReCaptcha validation into pre-existing data extraction """
        res = super(WebsiteForm, self).extract_data(model, values)
        is_pe_query_model = model.model == 'pe.query.cpe.form'
        if is_pe_query_model:
            invoice_id = request.env[model.sudo().model].get_document(values)
            res['record'] = {'invoice_id':invoice_id}
        return res
    #
    # def insert_record(self, request, model, values, custom, meta=None):
    #     res = super(WebsiteForm, self).insert_record(request, model, values, custom, meta)
    #     return res