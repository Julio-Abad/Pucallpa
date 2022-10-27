# -*- coding: utf-8 -*-
{
    'name': "Peruvian Sale",

    'summary': """
        sale""",

    'description': """
        sale
    """,

    'author': "grupo YACCK",
    'website': "http://www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','l10n_pe_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],
}
