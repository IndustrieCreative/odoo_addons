# -*- coding: utf-8 -*-
{
    'name': 'M2M and M2O orphan Attachments garbage collector',
    'summary': 'A garbage collector for orphan attachments from Many2many and Many2one fields.',
    'description': '',
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings', # https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '14.0.1.0.1',
    'depends': ['base'],
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'views/ir_attachment.xml',
        'views/ir_model.xml',
        'wizard/base_attachment_resfinder_views.xml',
    ],
}