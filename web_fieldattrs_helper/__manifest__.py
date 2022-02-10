# -*- coding: utf-8 -*-
{
    'name': 'Field Attrs Helper',
    'summary': """Manage field attrs from python (and more).""",
    'description': """
        A techical module to manage the attrs of the view field dynamically and directly from
        the server side. It also offers an alternative to record rules.""",
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings', # https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '14.0.1.0.0',
    'depends': ['base'],
    'application': False,
    'data': [
        'security/fieldattrs_helper_security.xml',
        'views/assets.xml',
        'views/ir_model_views.xml',
        'views/ir_ui_view_views.xml'
    ]
}