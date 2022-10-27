# -*- coding: utf-8 -*-
import json
from odoo import http

import requests

class PeruvianDocument(http.Controller):
    @http.route('/website/peruviandocument/', auth='public')
    def peruviandocument(self, **kw):
        datas = {}
        if kw.get('pe_doc_type', '') in ['1','6'] and kw.get('pe_doc_number'):
            try:
                datas = http.request.env['res.partner'].get_partner_from_ui(kw.get('pe_doc_type', ''),kw.get('pe_doc_number'))
            except Exception:
                pass
        return json.dumps(datas)

#     @http.route('/l10n_pe_website/l10n_pe_website/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_pe_website.listing', {
#             'root': '/l10n_pe_website/l10n_pe_website',
#             'objects': http.request.env['l10n_pe_website.l10n_pe_website'].search([]),
#         })
# 
#     @http.route('/l10n_pe_website/l10n_pe_website/objects/<model("l10n_pe_website.l10n_pe_website"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_pe_website.object', {
#             'object': obj
#         })
