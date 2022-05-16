# -*- coding: utf-8 -*-
{
    'name': "adv_booking",

    'summary': """
        Module pour calculer le TGC à partir de la marge""",

    'description': """
        Module pour calculer le TGC (6% de la marge)
    """,

    'author': "Advences",
    'website': "https://www.advences.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'AGPL-3'
}
