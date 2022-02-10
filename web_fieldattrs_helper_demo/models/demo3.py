# -*- coding: utf-8 -*-
from odoo import models, fields

class DemoModel3(models.Model):
    _name = 'web.fieldattrs.helper.demo3'
    _description = 'Demo model 3'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Name',
        # required = lambda self: self.browse(self._context.get('active_id')).trigger_field_1
    )

    target3_field_char = fields.Char(string = 'Char')
    target3_field_selection = fields.Selection(string='Selection', selection=[('val1', 'Value 1'),('val2', 'Value 2')])
    target3_field_m2o_demo1 = fields.Many2one(
        string='Many2one Demo 1',
        comodel_name = 'web.fieldattrs.helper.demo1',
        ondelete = 'set null',
    )
    target3_field_o2m_demo1 = fields.One2many(
        string='One2many Demo 1',
        comodel_name = 'web.fieldattrs.helper.demo1',
        inverse_name = 'target1_field_m2o_demo3',
    )
    target3_field_m2m_demo1 = fields.Many2many(
        string='Many2many Demo 1',
        comodel_name = 'web.fieldattrs.helper.demo1',
        relation = 'web_fieldattrs_helper_demo1_demo3_rel', # relation table name    
        column1 = 'demo3_id', # rel field to "this" table
        column2 = 'demo1_id', # rel field to "other" table
    )
