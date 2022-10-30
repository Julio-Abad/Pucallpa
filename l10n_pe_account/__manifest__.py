# -*- coding: utf-8 -*-
{
    'name': "Peruvian Invoice",

    'summary': """
        Peruvian Invoice""",

    'description': """
        Peruvian Invoice
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Uncategorized',
    'version': '0.2',
    'depends': [
        'account',
        'uom',
        'account_debit_note',
        'l10n_pe_toponyms',
        'l10n_pe_data',
        'l10n_pe_vat',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_currency_data.xml',
        'views/account_view.xml',
        'views/account_move_view.xml',
        'views/product_view.xml',
        'views/currency_view.xml',
        'views/uom_view.xml',
        'views/pe_payment_date_view.xml',
        'views/users_view.xml',
        'wizard/account_debit_note_view.xml',
        'wizard/account_move_reversal_view.xml',
    ],
}