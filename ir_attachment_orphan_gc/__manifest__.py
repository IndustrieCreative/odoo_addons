# -*- coding: utf-8 -*-
{
    'name': 'M2M and M2O orphan Attachments garbage collector',
    'summary': """A garbage collector for orphan attachments from Many2many and Many2one fields.""",
    'description': """
This module periodically deletes all orphaned attachments after the relationship with
a given model has been broken due to either deletion of the record or modification of
the field pointing to the attachment. The garbage collector is only activated on models
where there is an attribute <pre>_attachment_garbage_collector</pre> set to <pre>True</pre>.
<b>WARNING</b>: It only handles Many2any and Many2one fields pointing to "ir.attachment"
and with domain <pre>[('res_model', '=', _name)]</pre>.
    """,
    'license': 'OPL-1',
    'author': 'Walter Mantovani',
    'website': 'https://github.com/IndustrieCreative/odoo_addons',
    'category': 'Technical Settings', # https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    'version': '12.0.1.0.0',
    'depends': ['base'],
    'application': False,
    'data': ['views/ir_attachment.xml'],
}