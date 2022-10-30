# -*- coding: utf-8 -*-
{
    'name': "Peruvian Report",

    'summary': """
        Report, Account""",

    'description': """
        Invoice Reports
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/report_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}