# -*- coding: utf-8 -*-
import inspect
from odoo import api, fields, models

class DemoModel2(models.Model):
    _name = 'web.fieldattrs.helper.demo2'
    _inherit = ['web.fieldattrs.helper']
    _description = 'Demo model 2'
    _rec_name = 'name'
    _order = 'name'

    _FAH_FIELDS_PREFIX = 'asc2_'
    _FAH_ATTRS_FIELDS_DELIMITER = '&'
    _FAH_DEBUG_MODE = True

    name = fields.Char(
        string='Name',
        # required = lambda self: self.browse(self._context.get('active_id')).trigger_field_1
    )

    trigger2_readonly_field_char = fields.Boolean(string='RO Char')
    trigger2_readonly_field_selection = fields.Boolean(string='RO Selection')
    trigger2_readonly_field_m2o_demo1 = fields.Boolean(string='RO Many2one Demo 1')
    trigger2_readonly_field_o2m_demo1 = fields.Boolean(string='RO One2many Demo 1')
    trigger2_readonly_field_m2m_demo1 = fields.Boolean(string='RO Many2many Demo 1')
    
    trigger2_required_field_char = fields.Boolean(string='REQ Char')
    trigger2_required_field_selection = fields.Boolean(string='REQ Selection')
    trigger2_required_field_m2o_demo1 = fields.Boolean(string='REQ Many2one Demo 1')
    trigger2_required_field_o2m_demo1 = fields.Boolean(string='REQ One2many Demo 1')
    trigger2_required_field_m2m_demo1 = fields.Boolean(string='REQ Many2many Demo 1')
    
    trigger2_invisible_field_char = fields.Boolean(string='INV Char')
    trigger2_invisible_field_selection = fields.Boolean(string='INV Selection')
    trigger2_invisible_field_m2o_demo1 = fields.Boolean(string='INV Many2one Demo 1')
    trigger2_invisible_field_o2m_demo1 = fields.Boolean(string='INV One2many Demo 1')
    trigger2_invisible_field_m2m_demo1 = fields.Boolean(string='INV Many2many Demo 1')
    
    trigger2_column_invisible_o2m_field_demo1 = fields.Boolean(string='COL_INV One2many Demo 1')
    trigger2_column_invisible_m2m_field_demo1 = fields.Boolean(string='COL_INV Many2many Demo 1')

    trigger2_no_unlink = fields.Boolean(string='UNLINK not allowed')
    trigger2_no_write = fields.Boolean(string='WRITE not allowed')
    trigger2_no_read = fields.Boolean(string='READ not allowed')
    trigger2_no_create = fields.Boolean(string='CREATE not allowed')

    trigger2_readonly_calendar = fields.Boolean(string='RO Calendar')
    trigger2_required_calendar = fields.Boolean(string='REQ Calendar')
    trigger2_invisible_calendar = fields.Boolean(string='INV Calendar')

    trigger2_readonly_calendar_start_datetime = fields.Boolean(string='RO Start')
    trigger2_required_calendar_start_datetime = fields.Boolean(string='REQ Start')
    trigger2_invisible_calendar_start_datetime = fields.Boolean(string='INV Start')

    trigger2_readonly_calendar_stop_datetime = fields.Boolean(string='RO Stop')
    trigger2_required_calendar_stop_datetime = fields.Boolean(string='REQ Stop')
    trigger2_invisible_calendar_stop_datetime = fields.Boolean(string='INV Stop')

    trigger2_readonly_calendar_allday_boolean = fields.Boolean(string='RO Allday')
    trigger2_required_calendar_allday_boolean = fields.Boolean(string='REQ Allday')
    trigger2_invisible_calendar_allday_boolean = fields.Boolean(string='INV Allday')

    target2_field_char = fields.Char(string = 'Char')
    target2_field_selection = fields.Selection(string='Selection', selection=[('item1', 'Item 1'),('item2', 'Item 2')])
    target2_field_m2o_demo1 = fields.Many2one(
        string='Many2one Demo 1',
        comodel_name = 'web.fieldattrs.helper.demo1',
        ondelete = 'set null',
    )
    target2_field_o2m_demo1 = fields.One2many(
        string='One2many Demo 1',
        comodel_name = 'web.fieldattrs.helper.demo1',
        inverse_name = 'target1_field_m2o_demo2',
    )

    target2_field_m2m_demo1 = fields.Many2many(
        string='Many2many Demo 1',
        comodel_name = 'web.fieldattrs.helper.demo1',
        relation = 'web_fieldattrs_helper_demo1_demo2_rel', # relation table name    
        column1 = 'demo2_id', # rel field to "this" table
        column2 = 'demo1_id', # rel field to "other" table
    )

    target2_field_start_datetime = fields.Datetime(string='Calendar Start')
    target2_field_stop_datetime = fields.Datetime(string='Calendar Stop')
    target2_field_allday_boolean = fields.Boolean(string='Calendar Allday')

    _fah_trigger_fields = {
		'trigger2_readonly_field_char',
		'trigger2_readonly_field_selection',
		'trigger2_readonly_field_m2o_demo1',
		'trigger2_readonly_field_o2m_demo1',
		'trigger2_readonly_field_m2m_demo1',
		
		'trigger2_required_field_char',
		'trigger2_required_field_selection',
		'trigger2_required_field_m2o_demo1',
		'trigger2_required_field_o2m_demo1',
		'trigger2_required_field_o2m_demo1',
		
		'trigger2_invisible_field_char',
		'trigger2_invisible_field_selection',
		'trigger2_invisible_field_m2o_demo1',
		'trigger2_invisible_field_o2m_demo1',
		'trigger2_invisible_field_m2m_demo1',

		'trigger2_column_invisible_o2m_field_demo1',
		'trigger2_column_invisible_m2m_field_demo1',
        
        'trigger2_no_unlink',
        'trigger2_no_write',
        'trigger2_no_read',
        'trigger2_no_create',

        'trigger2_readonly_calendar_start_datetime',
        'trigger2_required_calendar_start_datetime',
        'trigger2_invisible_calendar_start_datetime',
        'trigger2_readonly_calendar_stop_datetime',
        'trigger2_required_calendar_stop_datetime',
        'trigger2_invisible_calendar_stop_datetime',
        'trigger2_readonly_calendar_allday_boolean',
        'trigger2_required_calendar_allday_boolean',
        'trigger2_invisible_calendar_allday_boolean',
    }
    _fah_model_target_fields = {
        'target2_field_char',
        'target2_field_selection',
        'target2_field_m2o_demo1',
        'target2_field_o2m_demo1',
        'target2_field_m2m_demo1',

        'target2_field_start_datetime',
        'target2_field_stop_datetime',
        'target2_field_allday_boolean',
    }

    _fah_model_target_nodes = {
        ('button', 'name', 'action_demo', '#BUTTON2#'),
    }

    _fah_embedded_target_fields = {
        ('target2_field_o2m_demo1.target1_field_selection', '#DEMO2TAG#')
    }

    # _fah_force_save_fields = {
    #     'target2_field_char',
    # }

    @api.fah_depends(*_fah_trigger_fields)
    def _fah_compute_helper_fields(self, attr_reg, eval_mode=False, override=False):
        
        if override != 'finish':
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='compute')
        
            field_types = ['char', 'selection', 'm2o_demo1', 'o2m_demo1', 'm2m_demo1']

            for r in self:

                for attr in self._FAH_ATTRS:
                    if attr != 'column_invisible':
    	                for field_type in field_types:
    	                    if r['trigger2_'+attr+'_field_'+field_type] == True:
    	                        attr_reg.set(['target2_field_'+field_type], attr, True, r)
    	                    else:
    	                        attr_reg.set(['target2_field_'+field_type], attr, False, r)

                cal_field_types = ['start_datetime', 'stop_datetime', 'allday_boolean']

                for attr in self._FAH_ATTRS:
                    if attr != 'column_invisible':
                        for cal_field_type in cal_field_types:
                            if r['trigger2_'+attr+'_calendar_'+cal_field_type] == True:
                                attr_reg.set(['target2_field_'+cal_field_type], attr, True, r)

                if r.trigger2_no_unlink == True:
                    attr_reg.set(0, 'no_unlink', True, r,
                        msg='You cannot delete the record because the trigger "UNLINK not allowed" is flagged!')

                if r.trigger2_column_invisible_o2m_field_demo1 == True:
                    attr_reg.set(
                        ['target2_field_o2m_demo1.target1_field_selection'],
                        'column_invisible', True, r)
    
        if override != 'compute':
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='finish')

    def action_demo(self):
        return