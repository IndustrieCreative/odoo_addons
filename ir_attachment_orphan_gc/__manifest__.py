{
    'name': 'M2M and M2O orphan Attachments garbage collector',
    'summary': 'A garbage collector for orphan attachments from Many2many and Many2one fields.',
    'description': '',
    'license': 'AGPL-3',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings',
    'version': '16.0.1.0.0',
    'depends': ['base', 'mail'],
    'application': False,
    'data': [
        'security/ir.model.access.csv',
        'views/ir_attachment.xml',
        'views/ir_model.xml',
        'wizard/base_attachment_resfinder_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ir_attachment_orphan_gc/static/src/js/thread.js',
            'ir_attachment_orphan_gc/static/src/js/chatter.js'
        ],
        'web.assets_qweb': [
            'ir_attachment_orphan_gc/static/src/xml/chatter_topbar.xml',
        ],
    }
}