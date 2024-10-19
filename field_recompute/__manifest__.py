# -*- coding: utf-8 -*-
{
    'name': 'Field recompute wizard ',
    'summary': """Force recomputing a stored computed field.""",
    'description': """With this wizard you can manually trigger the recomputation
                      of a computed stored field for one or all records of a model.""",
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings', # https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '16.0.1.0.0',
    'depends': ['base'],
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'wizard/field_recompute_dialog_view.xml'
    ],
}