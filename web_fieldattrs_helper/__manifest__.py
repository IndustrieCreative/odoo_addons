{
    'name': 'Field Attrs Helper',
    'summary': """Manage field attrs from python (and more).""",
    'description': """
        A techical module to manage the attrs of the view field dynamically and directly from
        the server side. It also offers an alternative to record rules.""",
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings',
    'version': '16.0.1.0.0',
    'depends': ['base'],
    'application': False,
    'data': [
        'security/fieldattrs_helper_security.xml',
        'views/ir_model_views.xml',
        'views/ir_ui_view_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'web_fieldattrs_helper/static/src/css/backend-style.css',
        ],
    }
}