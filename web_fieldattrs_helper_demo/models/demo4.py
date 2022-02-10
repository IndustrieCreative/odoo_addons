# -*- coding: utf-8 -*-
from odoo import models, fields

class DemoModel4(models.Model):
    _name = 'web.fieldattrs.helper.demo4'
    _description = 'Demo model 4'
    _rec_name = 'name'
    _order = 'name'
    _inherits = {'web.fieldattrs.helper.demo3': 'target4_field_m2o_demo3'}

    target4_field_char = fields.Char(string = 'Char (or.)')
    target4_field_selection = fields.Selection(string='Selection (or.)', selection=[('val1', 'Value 1'),('val2', 'Value 2')])
    target4_field_m2o_demo3 = fields.Many2one(
        string='Many2one Demo 3',
        comodel_name = 'web.fieldattrs.helper.demo3',
        required = True,
        ondelete = 'cascade',
    )
