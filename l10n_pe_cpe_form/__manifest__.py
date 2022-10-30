# -*- coding: utf-8 -*-
{
    'name': "Peruvian Electronic Voucher From",

    'summary': """
        cpe, website""",

    'description': """
        CPE form for search invoices
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Website',
    'version': '0.1',

    'depends': [
        'website_form',
        'l10n_pe_cpe'
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'data/website_data.xml',
        'views/assets.xml',
    ],
}
