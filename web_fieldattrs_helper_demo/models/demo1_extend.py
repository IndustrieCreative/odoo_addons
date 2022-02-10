# -*- coding: utf-8 -*-
import inspect
from odoo import api, fields, models

class DemoModel1Extend(models.Model):
    _inherit = 'web.fieldattrs.helper.demo1'

    trigger1_readonly_field_char = fields.Boolean(string='RO Char (I)')
    trigger1_readonly_field_text = fields.Boolean(string='RO Text (I)')
    trigger1_readonly_field_html = fields.Boolean(string='RO Html (I)')
    trigger1_readonly_field_date = fields.Boolean(string='RO Date (I)')
    trigger1_readonly_field_datetime = fields.Boolean(string='RO Datetime (I)')

    trigger1_required_field_char = fields.Boolean(string='REQ Char (I)')
    trigger1_required_field_text = fields.Boolean(string='REQ Text (I)')
    trigger1_required_field_html = fields.Boolean(string='REQ Html (I)')
    trigger1_required_field_date = fields.Boolean(string='REQ Date (I)')
    trigger1_required_field_datetime = fields.Boolean(string='REQ Datetime (I)')

    trigger1_invisible_field_char = fields.Boolean(string='INV Char (I)')
    trigger1_invisible_field_text = fields.Boolean(string='INV Text (I)')
    trigger1_invisible_field_html = fields.Boolean(string='INV Html (I)')
    trigger1_invisible_field_date = fields.Boolean(string='INV Date (I)')
    trigger1_invisible_field_datetime = fields.Boolean(string='INV Datetime (I)')

    target1_field_char = fields.Char(string = 'Char (I)')
    target1_field_text = fields.Text(string='Text (I)')
    target1_field_html = fields.Html(string='Html (I)')
    target1_field_date = fields.Date(string='Date (I)')
    target1_field_datetime = fields.Datetime(string='Datetime (I)')

    _fah_trigger_fields = {
        'trigger1_readonly_field_char',
        'trigger1_readonly_field_text',
        'trigger1_readonly_field_html',
        'trigger1_readonly_field_date',
        'trigger1_readonly_field_datetime',

        'trigger1_required_field_char',
        'trigger1_required_field_text',
        'trigger1_required_field_html',
        'trigger1_required_field_date',
        'trigger1_required_field_datetime',

        'trigger1_invisible_field_char',
        'trigger1_invisible_field_text',
        'trigger1_invisible_field_html',
        'trigger1_invisible_field_date',
        'trigger1_invisible_field_datetime',
    }
    _fah_model_target_fields = {
        'target1_field_char',
        'target1_field_text',
        'target1_field_html',
        'target1_field_date',
        'target1_field_datetime',
    }

    # _fah_attr_force_save_fields = {
    #     'target1_field_char',
    # }

    @api.fah_depends(*_fah_trigger_fields)
    def _fah_compute_helper_fields(self, attr_reg, eval_mode=False, override=False):
        
        if override != 'finish':
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='compute')

            field_types = ['char', 'text', 'html', 'date', 'datetime']

            for r in self:

                for attr in self._FAH_ATTRS:
                    if attr != 'column_invisible':
                        for field_type in field_types:
                            if r['trigger1_'+attr+'_field_'+field_type] == True:
                                attr_reg.set(['target1_field_'+field_type], attr, True, r)
                            else:
                                attr_reg.set(['target1_field_'+field_type], attr, False, r)

                if r.trigger1_no_unlink == True:
                    attr_reg.set(0, 'no_unlink', True, r,
                        msg='DEMO 1 EXT! You cannot delete the record because the trigger "UNLINK not allowed" is flagged!')

        if override != 'compute':
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='finish')
