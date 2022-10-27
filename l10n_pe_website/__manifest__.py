# -*- coding: utf-8 -*-
{
    'name': "Peruvian Website",

    'summary': """
        Website, Sale""",

    'description': """
        Website Sale
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'website_sale',
        'portal',
        'l10n_pe_vat',
        'website_partner',
        ],

    'data': [
        'views/portal_templates.xml',
        'views/templates.xml',
    ],
}
