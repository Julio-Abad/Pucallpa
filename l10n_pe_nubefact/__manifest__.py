# -*- coding: utf-8 -*-
{
    'name': "CPE Nubefact PSE",

    'summary': """
        Support Nubefact PSE Branch""",

    'description': """
        Nubefact Branch PSE
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'l10n_pe_eguide', 
        'l10n_pe_cpe', 
        'l10n_pe_cpe_branch'
        ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/users_view.xml',
    ],
}
