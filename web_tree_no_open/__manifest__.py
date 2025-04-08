{
    'name': 'Web Tree No Open',
    'version': '18.0.1.0.0',
    'author': 'Walter G. Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'license': 'AGPL-3',
    'category': 'Technical',
    'summary': 'Allows to force a "no open" attribute on native tree view',
    'description': """Although you can use the no_open attribute in a <tree>
                     node when defining an embedded list inside a form, this
                     does not work in native tree views. This module allows to
                     set "tree_no_open" class on tree tag to prevent the
                     corresponding record from being opened when clicking on it.""",
    'depends': ['base'],
    'application': False,
    'data': [],
    'assets': {
        'web.assets_backend': [
            'web_tree_no_open/static/src/js/list_render.js',
        ]
    }
}
