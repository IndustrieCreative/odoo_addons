# -*- coding: utf-8 -*-
{
    'name': 'Dynamic views inheritance',

    'summary': """
        A technical module to load inherited views dynamically.""",

    'description': """ 
        ...
    """,

    'license': 'OPL-1',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative',
    # check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'category': 'Technical Settings',
    'version': '12.0.1.0.0',

    'depends': ['base'],

    'application': False,

    # always loaded
    'data': ['security/asc_base_security.xml'],

}