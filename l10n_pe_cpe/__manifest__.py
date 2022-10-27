# -*- coding: utf-8 -*-
{
    'name': "Peruvian Electronic Voucher",

    'summary': """
        Peruvian Electronic Payment Voucher
    """,

    'description': """
        Peruvian Electronic Payment Voucher
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'l10n_pe_vat',
        'l10n_pe_toponyms',
        'l10n_pe_data',
        'l10n_pe_account',
        'account_edi',
        'account_edi_extended'
    ],

    # always loaded
    'data': [
        'security/cpe_security.xml',
        'security/ir.model.access.csv',
        'data/account_cpe_data.xml',
        'data/pe_cpe_data.xml',
        'views/account_move_view.xml',
        'views/account_view.xml',
        'views/company_view.xml',
        'views/product_view.xml',
        'views/report_invoice.xml',
        'views/account_portal_templates.xml',
        'views/res_config_settings_views.xml',
        'views/pe_cpe_view.xml',
        'wizard/pe_cpe_wizard_view.xml',
        'wizard/cpe_xml_bk_wizard_view.xml',
    ],
    'demo': [
    ],
}