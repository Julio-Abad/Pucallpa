# -*- coding: utf-8 -*-
{
    'name': "Base Branch",

    'summary': """
        Branch""",

    'description': """
        Branch
    """,

    'author': "grupo YACCK",
    'website': "http://www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/branch_groups.xml',
        'data/ir_module_category_data.xml',
        'views/account_move_view.xml',
        'views/account_view.xml',
        'views/assets.xml',
        'views/res_company_branch_views.xml',
        'views/users_view.xml',
        'views/report_templates.xml'
    ],
    # only loaded in demonstration mode
    'qweb': [
        "static/src/xml/base.xml",
        ],
}
