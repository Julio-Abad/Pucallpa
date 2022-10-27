# -*- coding: utf-8 -*-
{
    'name': "CPE Branch",

    'summary': """
        CPE, branch""",

    'description': """
        Add branch code for users
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['l10n_pe_cpe',
                'base_branch'],

    'data': [
        'views/company_branch_view.xml',
    ],
}
