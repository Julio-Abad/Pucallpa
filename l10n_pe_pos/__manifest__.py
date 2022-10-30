# -*- coding: utf-8 -*-
{
    'name': "Peruvian POS",

    'summary': """
        Peruvian Management POS""",

    'description': """
        Peruvian Management POS
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Localization/Peruvian',
    'version': '0.1',

    'depends': [
        'point_of_sale',
        'pos_default_partner',
        'pos_credit_note',
        'l10n_pe_vat',
        'l10n_pe_toponyms',
        'l10n_pe_account',
    ],

    'data': [
        'views/l10n_pe_pos_templates.xml',
        'views/pos_order_view.xml'
    ],
    'qweb': [
        'static/src/xml/Screens/ClientListScreen/ClientDetailsEdit.xml',
        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
    ],
}