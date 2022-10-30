# -*- coding: utf-8 -*-
{
    'name': "Peruvian POS Tickets",

    'summary': """
        Point of Sale""",

    'description': """
        Tickets from POS, for peruvian localization
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Localization/Peruvian',
    'version': '0.1',

    'depends': ['l10n_pe_pos_cpe'],

    'data': [
        'views/l10n_pe_pos_ticket_templates.xml',
    ],
    
    'qweb': [
        'static/src/xml/pos.xml'
    ],
}