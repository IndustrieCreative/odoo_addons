{
    'name': 'Tree no open',
    'version': '16.0.1.0.0',
    'author': 'EESTISOFT, ''Giulio Milani, ''Hideki Yamamoto',
    'category': 'Productivity',
    'website': 'https://github.com/EESTISOFT/ees_tree_no_open',
    'summary': 'Allows to set "no open" attribute on tree view',
    'description': """
Allows to set "tree_no_open" class on tree tag to prevent interraction upon row click.
Made with love.
NOTE: Taken from v12 original repo. It seems to work as it is.
@TODO: Check if it works on v15.0+. If not, see https://www.odoo.com/it_IT/forum/assistenza-1/prevent-popup-in-tree-view-226312
    """,
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'ees_tree_no_open/static/js/tree_no_open.js'
        ]
    }
}
