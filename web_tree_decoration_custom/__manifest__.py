{
    'name': 'List view custom decorators',
    'version': '15.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings',
    'depends': ['web'],
    'data': [],
    'installable': True,
    'assets': {
        'web.assets_backend': [
            'web_tree_decoration_custom/static/src/css/list_view.css',
            'web_tree_decoration_custom/static/src/js/list_renderer.js',
        ],
    }
}

# @SEE: https://github.com/Noviat/noviat-apps/tree/14.0/web_tree_decoration_underline
