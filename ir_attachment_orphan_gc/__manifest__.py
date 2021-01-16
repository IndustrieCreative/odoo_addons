# -*- coding: utf-8 -*-
{
    'name': 'M2M and M2O orphan Attachments garbage collector',
    'summary': 'A garbage collector for orphan attachments from Many2many and Many2one fields.',
    'description': '',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings', # https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '12.0.1.0.0',
    'depends': ['base'],
    'application': False,
    'data': ['views/ir_attachment.xml'],
}