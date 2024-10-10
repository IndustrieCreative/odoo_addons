# -*- coding: utf-8 -*-
{
    'name': 'Field Attrs Helper DEMO',
    'summary': """Demo module for Field Attrs Helper.""",
    'description': """A module to demonstrate and test functionalities.""",
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings', # https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '15.0.1.0.0',
    'depends': ['base', 'web_fieldattrs_helper'],
    'application': False,
    'data': [
        # 'security/asc_base_security.xml',
        'security/ir.model.access.csv',
        
        'views/demo1_views.xml',
        'views/demo2_views.xml',
        'views/demo3_views.xml',
        'views/demo4_views.xml',
        'views/demo1_extend_views.xml',
        'views/demo2_extend_views.xml',
        'views/menus.xml',
    ],
}