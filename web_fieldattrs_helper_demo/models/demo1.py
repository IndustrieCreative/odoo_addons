# -*- coding: utf-8 -*-

# @todo: Test write() check con:
#   - float field @ widget monetary
#   - binary field

# import inspect
from odoo import api, models, fields

class DemoModel1(models.Model):
    _name = 'web.fieldattrs.helper.demo1'
    _inherit = ['web.fieldattrs.helper']
    _description = 'Demo model 1'
    _rec_name = 'name'
    _order = 'name'

    _FAH_ATTRS_FIELDS_DELIMITER = '$'
    _FAH_DEBUG_MODE = True

    name = fields.Char(
        string='Name',
        # required = lambda self: self.browse(self._context.get('active_id')).trigger_field_1
    )

    # -------- TRIGGERS -------------------
    # MODEL
    # - - - - - -
    trigger1_readonly_field_integer = fields.Boolean(string='RO Integer')
    trigger1_readonly_field_float = fields.Boolean(string='RO Float')
    trigger1_readonly_field_monetary = fields.Boolean(string='RO Monetary')
    trigger1_readonly_field_selection = fields.Boolean(string='RO Selection')
    trigger1_readonly_field_m2o_demo2 = fields.Boolean(string='RO Many2one Demo 2')
    trigger1_readonly_field_m2o_demo3 = fields.Boolean(string='RO Many2one Demo 3')
    trigger1_readonly_field_o2m_demo2 = fields.Boolean(string='RO One2many Demo 2')
    trigger1_readonly_field_o2m_demo3 = fields.Boolean(string='RO One2many Demo 3')
    trigger1_readonly_field_m2m_demo2 = fields.Boolean(string='RO Many2many Demo 2')
    trigger1_readonly_field_m2m_demo3 = fields.Boolean(string='RO Many2many Demo 3')
    
    trigger1_required_field_integer = fields.Boolean(string='REQ Integer')
    trigger1_required_field_float = fields.Boolean(string='REQ Float')
    trigger1_required_field_monetary = fields.Boolean(string='REQ Monetary')
    trigger1_required_field_selection = fields.Boolean(string='REQ Selection')
    trigger1_required_field_m2o_demo2 = fields.Boolean(string='REQ Many2one Demo 2')
    trigger1_required_field_m2o_demo3 = fields.Boolean(string='REQ Many2one Demo 3')
    trigger1_required_field_o2m_demo2 = fields.Boolean(string='REQ One2many Demo 2')
    trigger1_required_field_o2m_demo3 = fields.Boolean(string='REQ One2many Demo 3')
    trigger1_required_field_m2m_demo2 = fields.Boolean(string='REQ Many2many Demo 2')
    trigger1_required_field_m2m_demo3 = fields.Boolean(string='REQ Many2many Demo 3')
    
    trigger1_invisible_field_integer = fields.Boolean(string='INV Integer')
    trigger1_invisible_field_float = fields.Boolean(string='INV Float')
    trigger1_invisible_field_monetary = fields.Boolean(string='INV Monetary')
    trigger1_invisible_field_selection = fields.Boolean(string='INV Selection')
    trigger1_invisible_field_m2o_demo2 = fields.Boolean(string='INV Many2one Demo 2')
    trigger1_invisible_field_m2o_demo3 = fields.Boolean(string='INV Many2one Demo 3')
    trigger1_invisible_field_o2m_demo2 = fields.Boolean(string='INV One2many Demo 2')
    trigger1_invisible_field_o2m_demo3 = fields.Boolean(string='INV One2many Demo 3')
    trigger1_invisible_field_m2m_demo2 = fields.Boolean(string='INV Many2many Demo 2')
    trigger1_invisible_field_m2m_demo3 = fields.Boolean(string='INV Many2many Demo 3')
    

    # O2M DEMO 2 EMBEDDEDS
    # - - - - - -
    # Field
    trigger1_readonly_o2m_field_demo2 = fields.Boolean(string='RO FIELD Many2many Demo 3')
    trigger1_required_o2m_field_demo2 = fields.Boolean(string='REQ FIELD Many2many Demo 3')
    trigger1_invisible_o2m_field_demo2 = fields.Boolean(string='INV Many2many FIELD Demo 3')
    trigger1_column_invisible_o2m_field_demo2 = fields.Boolean(string='COL_INV One2many Demo 2')
    # Button
    trigger1_invisible_o2m_button_demo2 = fields.Boolean(string='INV Many2many BUTTON Demo 3')
    trigger1_column_invisible_o2m_button_demo2 = fields.Boolean(string='COL_INV Button Many2many Demo 3')

    # OTHER EMBEDDEDS
    trigger1_column_invisible_o2m_field_demo3 = fields.Boolean(string='COL_INV One2many Demo 3')
    trigger1_column_invisible_m2m_field_demo2 = fields.Boolean(string='COL_INV Many2many Demo 2')
    trigger1_column_invisible_m2m_field_demo3 = fields.Boolean(string='COL_INV Many2many Demo 3')
    # - - - - - -

    # TAG
    trigger1_readonly_tag_foo = fields.Boolean(string='RO #FOO# TAG')
    trigger1_required_tag_foo = fields.Boolean(string='REQ #FOO# TAG')
    trigger1_invisible_tag_foo = fields.Boolean(string='INV #FOO# TAG')
    trigger1_column_invisible_tag_foo = fields.Boolean(string='COL_INV #FOO# TAG')

    # OPS
    trigger1_no_unlink = fields.Boolean(string='UNLINK not allowed')
    trigger1_no_write = fields.Boolean(string='WRITE not allowed')
    trigger1_no_read = fields.Boolean(string='READ not allowed')
    trigger1_no_create = fields.Boolean(string='CREATE not allowed')
    

    # -------- TARGETS -------------------
    target1_field_integer = fields.Integer(string='Integer')
    target1_field_float = fields.Float(string='Float')
    target1_field_monetary = fields.Monetary(string='Monetary', currency_field='currency_id')
    target1_field_selection = fields.Selection(string='Selection', selection=[('val1', 'Value 1'),('val2', 'Value 2')], default='val1')
    target1_field_m2o_demo2 = fields.Many2one(
        string='Many2one Demo 2',
        comodel_name = 'web.fieldattrs.helper.demo2',
        ondelete = 'set null',
    )
    target1_field_m2o_demo3 = fields.Many2one(
        string='Many2one Demo 3',
        comodel_name = 'web.fieldattrs.helper.demo3',
        ondelete = 'set null',
    )
    target1_field_o2m_demo2 = fields.One2many(
        string='One2many Demo 2',
        comodel_name = 'web.fieldattrs.helper.demo2',
        inverse_name = 'target2_field_m2o_demo1',
    )
    target1_field_o2m_demo3 = fields.One2many(
        string='One2many Demo 3',
        comodel_name = 'web.fieldattrs.helper.demo3',
        inverse_name = 'target3_field_m2o_demo1',
    )
    target1_field_m2m_demo2 = fields.Many2many(
        string='Many2many Demo 2',
        comodel_name = 'web.fieldattrs.helper.demo2',
        relation = 'web_fieldattrs_helper_demo1_demo2_rel', # relation table name    
        column1 = 'demo1_id', # rel field to "this" table
        column2 = 'demo2_id', # rel field to "other" table
    )
    target1_field_m2m_demo3 = fields.Many2many(
        string='Many2many Demo 3',
        comodel_name = 'web.fieldattrs.helper.demo3',
        relation = 'web_fieldattrs_helper_demo1_demo3_rel', # relation table name    
        column1 = 'demo1_id', # rel field to "this" table
        column2 = 'demo3_id', # rel field to "other" table
    )

    currency_id = fields.Many2one(related='company_id.currency_id')
    active = fields.Boolean(default = True)
    company_id = fields.Many2one(
        string = 'Company',
        comodel_name = 'res.company',
        ondelete = 'restrict',
        index = True,
        required = True,
        default = lambda self: self.env.company,
        # readonly = True
    )

    _fah_trigger_fields = {
        'trigger1_readonly_field_integer',
        'trigger1_readonly_field_float',
        'trigger1_readonly_field_monetary',
        'trigger1_readonly_field_selection',
        'trigger1_readonly_field_m2o_demo2',
        'trigger1_readonly_field_m2o_demo3',
        'trigger1_readonly_field_o2m_demo2',
        'trigger1_readonly_field_o2m_demo3',
        'trigger1_readonly_field_m2m_demo2',
        'trigger1_readonly_field_m2m_demo3',
        
        'trigger1_required_field_integer',
        'trigger1_required_field_float',
        'trigger1_required_field_monetary',
        'trigger1_required_field_selection',
        'trigger1_required_field_m2o_demo2',
        'trigger1_required_field_m2o_demo3',
        'trigger1_required_field_o2m_demo2',
        'trigger1_required_field_o2m_demo3',
        'trigger1_required_field_m2m_demo2',
        'trigger1_required_field_m2m_demo3',
        
        'trigger1_invisible_field_integer',
        'trigger1_invisible_field_float',
        'trigger1_invisible_field_monetary',
        'trigger1_invisible_field_selection',
        'trigger1_invisible_field_m2o_demo2',
        'trigger1_invisible_field_m2o_demo3',
        'trigger1_invisible_field_o2m_demo2',
        'trigger1_invisible_field_o2m_demo3',
        'trigger1_invisible_field_m2m_demo2',
        'trigger1_invisible_field_m2m_demo3',
        
        'trigger1_readonly_o2m_field_demo2',
        'trigger1_required_o2m_field_demo2',
        'trigger1_invisible_o2m_field_demo2',
        'trigger1_column_invisible_o2m_field_demo2',

        'trigger1_invisible_o2m_button_demo2',
        'trigger1_column_invisible_o2m_button_demo2',

        'trigger1_column_invisible_o2m_field_demo3',
        'trigger1_column_invisible_m2m_field_demo2',
        'trigger1_column_invisible_m2m_field_demo3',
        
        'trigger1_readonly_tag_foo',
        'trigger1_required_tag_foo',
        'trigger1_invisible_tag_foo',
        'trigger1_column_invisible_tag_foo',

        'trigger1_no_unlink',
        'trigger1_no_write',
        'trigger1_no_read',
        'trigger1_no_create',

        # 'target1_field_selection', # Be careful because you can block the view!!!
    }

    # @todo: ? tag check: when doing a set-attr check that the tag is used by some element!

    _fah_model_target_fields = {
        ('target1_field_integer'),
        'target1_field_float',
        'target1_field_monetary',
        ('target1_field_selection', '#FOO#'),
        'target1_field_m2o_demo2',
        'target1_field_m2o_demo3',
        'target1_field_o2m_demo2',
        'target1_field_o2m_demo3',
        'target1_field_m2m_demo2',
        'target1_field_m2m_demo3',
        
        # 'trigger1_readonly_field_selection', # Be careful because you can block the view!!!
    }

    _fah_embedded_target_fields = {
        ('target1_field_o2m_demo2.target2_field_selection', '#FOO#'),
        ('target1_field_o2m_demo3.target3_field_selection'),
        'target1_field_m2m_demo2.target2_field_selection',
        'target1_field_m2m_demo3.target3_field_selection',
    }

    _fah_force_save_fields = {
        # 'target1_field_selection',
    }

    _fah_force_null_fields = {
        # 'target1_field_selection',
    }

    _fah_model_target_nodes = {
        ('group', 'name', 'group-target-1', '#FOO#'),
        ('div', 'id', 'div-target-1', '#USER MESSAGE#'),
        ('div', 'name', 'div-target-2', '#ADMIN MESSAGE#'),
        ('button', 'name', 'action_demo', '#FOO#'),
    }
    _fah_embedded_target_nodes = {
        ('target1_field_o2m_demo2', 'button', 'name', 'action_demo', '#BUTTON-EMBEDDED#'),
    }

    @api.fah_depends(*_fah_trigger_fields)
    def _fah_compute_helper_fields(self, attr_reg, eval_mode=False, override=False):

        if override != 'finish':
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='compute')
        
            field_types = ['integer', 'float', 'monetary', 'selection', 'm2o_demo2', 'm2o_demo3', 'o2m_demo2', 'o2m_demo3', 'm2m_demo2', 'm2m_demo3']


            for r in self:

                # MODEL ATTRS TEST
                for attr in self._FAH_ATTRS:
                    if attr != 'column_invisible':
                        for field_type in field_types:
                            if r['trigger1_'+attr+'_field_'+field_type] == True:
                                attr_reg.set(['target1_field_'+field_type], attr, True, r,
                                    msg='This message is customisable.')
                
                # RULE OVERWRITE TEST
                if r.trigger1_required_field_selection == True:
                    attr_reg.set(['target1_field_selection'], 'required', True, r,
                        msg='no-check')
    
                # MODEL OPS TEST
                for op in self._FAH_OPS:
                    if r['trigger1_'+op] == True:
                        attr_reg.set(0, op, True, r,
                            msg=f'''DEMO 1! The record has the attribute [ {op} ] set to "True!''')

                # MODEL #FOO# TAG TEST
                if r.trigger1_readonly_tag_foo == True:
                    attr_reg.set(['#FOO#'], 'readonly', True, r,
                        msg='Because the field is tagged #FOO#!')
                if r.trigger1_required_tag_foo == True:
                    attr_reg.set(['#FOO#'], 'required', True, r,
                        msg='Because the field is tagged #FOO#!')
                if r.trigger1_invisible_tag_foo == True:
                    attr_reg.set(['#FOO#'], 'invisible', True, r,
                        msg='Because the field is tagged #FOO#!')
                if r.trigger1_column_invisible_tag_foo == True:
                    attr_reg.set(['#FOO#'], 'column_invisible', True, r)


                # EMBEDDED FIELD TEST
                if r.trigger1_readonly_o2m_field_demo2 == True:
                    attr_reg.set(['target1_field_o2m_demo2.target2_field_selection'], 'readonly', True, r)
                if r.trigger1_required_o2m_field_demo2 == True:
                    attr_reg.set(['target1_field_o2m_demo2.target2_field_selection'], 'required', True, r)
                if r.trigger1_invisible_o2m_field_demo2 == True:
                    attr_reg.set(['target1_field_o2m_demo2.target2_field_selection'], 'invisible', True, r)
                if r.trigger1_column_invisible_o2m_field_demo2 == True:
                    attr_reg.set(['target1_field_o2m_demo2.target2_field_selection'], 'column_invisible', True, r)

                # EMBEDDED #BUTTON-EMBEDDED# TAG TEST
                if r.trigger1_invisible_o2m_button_demo2 == True:
                    attr_reg.set(['#BUTTON-EMBEDDED#'], 'invisible', True, r)
                if r.trigger1_column_invisible_o2m_button_demo2 == True:
                    attr_reg.set(['#BUTTON-EMBEDDED#'], 'column_invisible', True, r)


                # OTHER EMBEDDED FIELD COLUMN INVISIBLE TEST
                if r.trigger1_column_invisible_o2m_field_demo3 == True:
                    attr_reg.set(
                        ['target1_field_o2m_demo3.target3_field_selection'],
                        'column_invisible', True, r)
                if r.trigger1_column_invisible_m2m_field_demo2 == True:
                    attr_reg.set(
                        ['target1_field_m2m_demo2.target2_field_selection'],
                        'column_invisible', True, r)
                if r.trigger1_column_invisible_m2m_field_demo3 == True:
                    attr_reg.set(
                        ['target1_field_m2m_demo3.target3_field_selection'],
                        'column_invisible', True, r)


                # EXTERNAL CONDITION BASED TESTS
                # @todo: Implement tests with conditions involving readings from other models.
                #        In this case, computed fields, related...
                #        More problematic case, when a field X becomes REQUIRED due to an
                #        external condition.
                #        For example, if the condition depends on a computed field Y (internal),
                #        which depends on a field Z of a comodel (external), when the field Z is
                #        changed, it should give an error saying that the field X is (become) required.
                #        And so it locks the operation on the comodel (external model).
                #        ?? In this case, do we have enough information to unlock the situation
                #           using the message available in the rules ??

                # USER BASED TESTS
                if self.env.user.has_group('web_fieldattrs_helper.fah_global_bypass_group'):
                    attr_reg.set(['#USER MESSAGE#'], 'invisible', True, r)
                else:
                    attr_reg.set(['#ADMIN MESSAGE#'], 'invisible', True, r)

        if override != 'compute':
            super()._fah_compute_helper_fields(attr_reg, eval_mode=eval_mode, override='finish')
        
    def action_demo(self):
        return
