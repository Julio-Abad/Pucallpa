# -*- coding: utf-8 -*-
{
    "name": u"Modificaciones Facturación Electrónica",
    "summary": u"Modificaciones / Correcciones de la Facturación Electrónica V14.0",
    "version": "14.0.0.0",
    "category": 'Tools',
    "website": "https://www.alwaperu.pe",
    'description': u"""
        DESCRIPCION:
        - Modificaciones / Correcciones de la Facturación Electrónica V14.0
    """,
    'author': "Alwa Peru",
    'license': 'AGPL-3',
    "depends": [
        'l10n_pe_cpe',
        'sale',
        'account',
        'mail'
    ],
    "data": [
        'data/mail_template_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
