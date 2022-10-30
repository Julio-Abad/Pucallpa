# -*- coding: utf-8 -*-
{
    'name': "Validate RUC in Billing",

    'summary': """
        Validate RUC in Billing
        """,

    'description': """
    Este addon valida el ruc de los clientes con la SUNAT al validar una factura
    """,

    'author': "Alwaperu",
    'website': "",

    'category': 'Localization/Peruvian',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'l10n_pe_vat',
        'account',
    ],

    # always loaded
    'data': [
    ],
}
