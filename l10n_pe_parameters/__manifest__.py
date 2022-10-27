# -*- coding: utf-8 -*-
# Copyright 2019 Alwa Peru (https://www.alwaperu.pe)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Parametrizaciones y Representacion Impresa Sunat",
    "summary": "Personalizaciones de representacion Impresa Sunat y parametrizaciones el picking",
    "version": "14.0.0.0",
    "category": "Invoice",
    "website": "https://www.alwaperu.pe",
    'description': """
        DESCRIPCION:
        - Personalizaciones de representacion Impresa Sunat Facturas, Boletas, NC, ND.
    """,
    'author': "Alwa Peru",
    'license': 'AGPL-3',
    "depends": [
        'base',
        'fleet',
        'sale_stock',
        'purchase_stock',
        'l10n_pe_cpe',
        'l10n_pe_eguide',
        'automatic_payment_fees'
    ],

    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/paperformat.xml',
        'data/einvoice_12_data.xml',
        'data/motivo_reclamo.xml',
        'views/parameters_views.xml',
        'views/account_move_views.xml',
        'report/report_cpe_invoice.xml',
        'report/report_cpe_picking.xml',
        'data/mail_template_data.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
