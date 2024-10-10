{
    'name': 'SQL Constraints Manager',
    'summary': """Allow to remove SQL Constraints.""",
    'description': """With this wizard you can shoq and manually remove SQL 
                      Constraints.""",
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings',
    'version': '15.0.1.0.0',
    'depends': ['base', 'field_recompute'],
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'wizard/sql_constraint_views.xml'
    ],
}