# -*- coding: utf-8 -*-

import logging
import json
from lxml import html
# from textwrap import dedent
from inspect import cleandoc as dedent
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from .. attr_registry import FahAttrRegistry, _msg_prefix

_logger = logging.getLogger(__name__+' | '+_msg_prefix +' :\n')

# @todo: - use tuples instead of lists wherever possible!
#        - use set instead of list wherever you need to store
#          a lot of elements and it is possible! (for performance)

# @todo: command "all-fields" to put all model fields in targets! at this point
#        you make everything readonly, for example.
# @todo: ?? all fields of the view become readonly if no_write == True!
#         (not possible if not all fields are targets!)
#        >> to be added when writing helper fields, at the bottom, if no_write == True
#           then all fields appear in the readonly helper.
          
# @todo: shorten long lines in messages with:
#        '''abcd...fg \
#        h...xyz'''
#        (eliminate the newline with an escaping backslash)

# @todo: use the check
#  !-->  if not self._abstract:
#        wherever it is needed! If they use it in the core, it means that there
#        is a risk of performing operations on the abstract model, which should
#        always be "inert".

# @todo: implement the "only-check" message, to perfoorm only the check,
#        but without inject the attrs into the view.

# @todo: ?? Integrate the attr_reg directly into the recordset, since their "lifetime"
#           is the same. Create an ad-hoc "slot" in the model that implements the helper.

# @todo: √ If the field is defined "readonly", "required" o "invisible"(?)
#          in python field definition, then set that value if that attr is not in the attr_reg.
#        √ Add a "fah_force_save" argument in field definition.

# AbstractModel to be inherited for dynamic management of field attributes in views
class FieldAttrsHelper(models.AbstractModel):
    _name = 'web.fieldattrs.helper'
    _description = 'Field Attrs Helper (FAH)'
    
    #==================================================
    # ** MODEL INIT **
    # Dynamically computes model attributes
    def __init__(self, pool, cr):
        init_res = super(FieldAttrsHelper, self).__init__(pool, cr)

        # Check that the delimiters are different
        if self._FAH_ATTRS_FIELDS_DELIMITER == self._FAH_ATTRS_TAG_DELIMITER:
            raise ValueError(
                _msg_prefix + f' Model [ {self._name} ] - The values of the '
                'delimiters _FAH_ATTRS_FIELDS_DELIMITER and _FAH_ATTRS_TAG_DELIMITER '
                'must be different!'
            )

        # Creates attributes (on the instance) that must take custom values
        # based on overrides made on models that inherit this abstract model.
        # type(self)._FAH_ATTRS_FIELDS = [self._FAH_FIELDS_PREFIX+attr+'_targets' for attr in self._FAH_ATTRS]
        # type(self)._FAH_ATTRS_TUPLES = list(zip(self._FAH_ATTRS, self._FAH_ATTRS_FIELDS)) # (attr, helper field name)
        # @todo: does it make a difference between reading from self._FAH_ATTRS_FIELDS and type(self)._FAH_ATTRS_FIELDS ??
        # type(self)._FAH_OPS_FIELDS = [self._FAH_FIELDS_PREFIX+op for op in self._FAH_OPS]
        # type(self)._FAH_OPS_MSG_FIELDS = [self._FAH_FIELDS_PREFIX+op+'_msg' for op in self._FAH_OPS]
        # type(self)._FAH_OPS_TUPLES = list(zip(self._FAH_OPS, self._FAH_OPS_FIELDS, self._FAH_OPS_MSG_FIELDS)) # (attr, helper field name, message helper field name)

        # type(self)._FAH_BYPASS_FIELD = self._FAH_FIELDS_PREFIX+'bypass'
        # type(self)._FAH_STARTER_FIELD = self._FAH_FIELDS_PREFIX+'starter'
        # type(self)._FAH_FIRST_TRIGGER_FIELD = self._FAH_FIELDS_PREFIX+'first_trigger'
        # type(self)._FAH_BYPASS_GROUPS_ALL = [self._FAH_BYPASS_CORE_GROUP, *self._FAH_BYPASS_GROUPS_ADD]
        
        # type(self)._FAH_BLACKLIST_CORE_FIELDS = [
        #     *type(self)._FAH_ATTRS_FIELDS,
        #     *type(self)._FAH_OPS_FIELDS,
        #     *type(self)._FAH_OPS_MSG_FIELDS,
        #     type(self)._FAH_BYPASS_FIELD
        # ]
        # type(self)._FAH_FIELD_REGISTRY = dict()
        # type(self)._FAH_COMPUTE_MRO_CHAIN = dict()

        # Set the onchange starter field dinamically
        # self._FAH_FIELD_REGISTRY['starter_field']
        # self._FAH_FIELD_REGISTRY['first_trigger_field']
        @api.onchange(self._FAH_STARTER_FIELD)
        def _fah_onchange_starter_field(self):
            self[self._FAH_FIRST_TRIGGER_FIELD] = not self[self._FAH_FIRST_TRIGGER_FIELD]
        type(self)._fah_onchange_starter_field = _fah_onchange_starter_field
        # FieldAttrsHelper._fah_onchange_starter_field = _fah_onchange_starter_field
        # setattr(self, '_fah_onchange_starter_field', _fah_onchange_starter_field)
        return init_res

    # def init(self):
    #     @api.onchange(self._FAH_STARTER_FIELD)
    #     def _fah_onchange_starter_field(self):
    #         self[self._FAH_FIRST_TRIGGER_FIELD] = not self[self._FAH_FIRST_TRIGGER_FIELD]
    #     self._fah_onchange_starter_field = _fah_onchange_starter_field

    # @property
    # def _fah_onchange_starter_field(self):
    #     return self._FAH_FIELD_REGISTRY.get('onchange_starter_field')

    # @_fah_onchange_starter_field.setter
    # def _fah_onchange_starter_field(self, onchange_fn):
    #     self._FAH_FIELD_REGISTRY = {'onchange_starter_field': onchange_fn}

    @property
    def _FAH_ATTRS_FIELDS(self):
        return [self._FAH_FIELDS_PREFIX + attr + '_targets' for attr in self._FAH_ATTRS]

    @property
    def _FAH_ATTRS_TUPLES(self):
        return list(zip(self._FAH_ATTRS, self._FAH_ATTRS_FIELDS))  # (attr, helper field name)

    @property
    def _FAH_OPS_FIELDS(self):
        return [self._FAH_FIELDS_PREFIX+op for op in self._FAH_OPS]

    @property
    def _FAH_OPS_MSG_FIELDS(self):
        return [self._FAH_FIELDS_PREFIX+op+'_msg' for op in self._FAH_OPS]

    @property
    def _FAH_OPS_TUPLES(self):
        return list(zip(self._FAH_OPS, self._FAH_OPS_FIELDS, self._FAH_OPS_MSG_FIELDS))  # (attr, helper field name, message helper field name)

    @property
    def _FAH_BYPASS_FIELD(self):
        return self._FAH_FIELDS_PREFIX+'bypass'

    @property
    def _FAH_STARTER_FIELD(self):
        return self._FAH_FIELDS_PREFIX+'starter'

    @property
    def _FAH_FIRST_TRIGGER_FIELD(self):
        return self._FAH_FIELDS_PREFIX+'first_trigger'

    @property
    def _FAH_BYPASS_GROUPS_ALL(self):
        # return [self._FAH_BYPASS_CORE_GROUP] + self._FAH_BYPASS_GROUPS_ADD
        return [self._FAH_BYPASS_CORE_GROUP, *self._FAH_BYPASS_GROUPS_ADD]

    @property
    def _FAH_BLACKLIST_CORE_FIELDS(self):
        # return self._FAH_ATTRS_FIELDS + self._FAH_OPS_FIELDS + self._FAH_OPS_MSG_FIELDS + [self._FAH_BYPASS_FIELD]
        return [
            *self._FAH_ATTRS_FIELDS,
            *self._FAH_OPS_FIELDS,
            *self._FAH_OPS_MSG_FIELDS,
            self._FAH_BYPASS_FIELD
        ]

    @property
    def _FAH_FIELD_REGISTRY(self):
        if not self._GLOBAL_FAH_FIELD_REGISTRY.get(self._name):
            self._GLOBAL_FAH_FIELD_REGISTRY[self._name] = dict()
        return self._GLOBAL_FAH_FIELD_REGISTRY[self._name]

    @_FAH_FIELD_REGISTRY.setter
    def _FAH_FIELD_REGISTRY(self, value):
        if not self._GLOBAL_FAH_FIELD_REGISTRY.get(self._name):
            self._GLOBAL_FAH_FIELD_REGISTRY[self._name] = dict()
        self._GLOBAL_FAH_FIELD_REGISTRY[self._name].update(value)

    #=================================================
    # ** MODEL INIT **
    # When the module setup is complete and the ORM is available,
    # compile the register with the declarations of the trigger/target
    # fields and target nodes.
    @api.model
    def _setup_complete(self):
        res = super(FieldAttrsHelper, self)._setup_complete()

        model_target_fields, model_target_field_tags = self._fah_get_model_target_fields_and_tags()
        self._FAH_FIELD_REGISTRY = {
            'trigger_fields': self._fah_get_trigger_fields(), # set
            'model_target_fields': model_target_fields, # dict
            'model_target_field_tags': model_target_field_tags, # dict
            'embedded_target_fields': self._fah_get_embedded_target_fields(), # dict
            'model_target_nodes': self._fah_get_model_target_nodes(), # dict
            'embedded_target_nodes': self._fah_get_embedded_target_nodes(), # dict
            'force_save_fields': self._fah_get_force_save_fields(), # set
            'force_null_fields': self._fah_get_force_null_fields() # set
        }
        return res

    # Dynamically adds all the necessary helper fields to the model
    @api.model
    def _add_inherited_fields(self):

        super(FieldAttrsHelper, self)._add_inherited_fields()
        
        if self._name != 'web.fieldattrs.helper':
        # Otherwise it also creates the fields with the abstract model prefix...
        # (I still don't understand why...)

            # Internal function to add fields safely.
            def add_helper(name, field):
                if name not in self._fields:
                    self._add_field(name, field)
                else:
                    raise ValueError(_msg_prefix + f' Model [ {self._name} ] - The field {field_name} already exists!')

            # Attrs helper fields
            for field_name in self._FAH_ATTRS_FIELDS:
                add_helper(field_name, fields.Char(
                    compute = '_fah_compute_helper_fields',
                    store = False,
                    compute_sudo = True,
                    default = '[]'
                ))
            # Ops helper fields
            if self._FAH_CREATE_OPS_FIELDS:
                for field_name in self._FAH_OPS_FIELDS:
                    add_helper(field_name, fields.Boolean(
                        compute = '_fah_compute_helper_fields',
                        store = False,
                        compute_sudo = True,
                        default = False,
                    ))
                for field_name in self._FAH_OPS_MSG_FIELDS:
                    add_helper(field_name, fields.Char(
                        compute = '_fah_compute_helper_fields',
                        store = False,
                        compute_sudo = True,
                        default = '/'
                    ))
        
            # Bypass field
            add_helper(self._FAH_BYPASS_FIELD, fields.Boolean(
                store = True, # Must be stored!
                # NOTE: Groups are only set at the view level and the check on
                #       writing to this field is done directly at write().
                #       Don't set the groups here becaise it will cause secondary
                #       problems that are not currently handled.
                # groups = ','.join(self._FAH_BYPASS_GROUPS_ALL),
                default = False,
                help = 'Field to bypass checks on this single record.',
            ))
            add_helper(self._FAH_STARTER_FIELD, fields.Boolean(
                store = False, # Must be not stored!
                default = True,
                help = 'Field to trigger the onchange method that will modify the _FAH_FIRST_TRIGGER_FIELD on new records.',
            ))
            add_helper(self._FAH_FIRST_TRIGGER_FIELD, fields.Boolean(
                store = False, # Must be not stored!
                default = False,
                help = 'Field to start the first computation of the helper fields on new records.',
            ))

    def _valid_field_parameter(self, field, name):
        return name == 'fah_force_save' or super()._valid_field_parameter(field, name)

    #============================================================
    # ** MODEL INIT **
    # Add attributes to the model that are used as parameters.
    # NOTE: All attributes may be overridden except where indicated otherwise.

    # Types of "attrs" and "ops" you want to manage
    _FAH_ATTRS = ['readonly', 'required', 'invisible', 'column_invisible'] # NOTE: leave it as list() !
    _FAH_OPS = ['no_read', 'no_write', 'no_create', 'no_unlink']
    # Type of views you want to inject the attrs into
    _FAH_VIEWS = ['form', 'tree', 'embedded_form', 'embedded_tree']
    # Prefix of helper fields, customisable to avoid name collisions.
    _FAH_FIELDS_PREFIX = 'fah_'
    # Target field name delimiters, to avoid false positives in the "like" (e.g. "name" and "surname")
    # Please note that the fields delimiter and the tag delimiter must be different.
    # Be careful to use only ASCII symbols, not alphanumeric characters and not uderscore (_).
    # e.g. @ # $ (tested)
    _FAH_ATTRS_FIELDS_DELIMITER = '@'
    # NOTE: Tags must not contain dots (.)
    _FAH_ATTRS_TAG_DELIMITER = '#'

    # List of security group names that can bypass the helper.
    # These groups are added automatically to 'web_fieldattrs_helper.fah_global_bypass_group'
    # which is added automatically and is mandatory.
    # NOTE: To display the bypass field, in addition to being within one
    #       of these groups, developer mode must also be activated.
    _FAH_BYPASS_GROUPS_ADD = []
    # **==** Start No edit/override **==**
    _FAH_BYPASS_CORE_GROUP = 'web_fieldattrs_helper.fah_global_bypass_group'
    # **==** Stop No edit/override **==**

    # Enables/disables the recomputation of both attrs and ops helper fields
    # (as there is only one function).
    # NOTE: It does not disable the triggering of the compute function,
    #       but writes the default values into the helper fields, inhibiting
    #       the behaviour of the "attrs" in all views of the model.
    _FAH_HELPER_FIELDS_COMPUTE = True
        
    # Enables/disables the injection of helper fields and "attrs" into target fields.
    # NOTE: Currently only use _FAH_XML_INJECT and never deactivate _FAH_XML_INJECT_ATTRS.
    _FAH_XML_INJECT = True
    # Activates/deactivates ONLY the injection of "attrs" into the target fields.
    # @todo: If we no longer need to re-implement the ability to manually define
    #        attrs in the views, remove this attribute.
    #        There will only be _FAH_XML_INJECT.
    _FAH_XML_INJECT_ATTRS = True
    
    # Create or not the fields for OPS and those for the respective messages.
    # To be used only if you need to show information about OPS in the UI.
    _FAH_CREATE_OPS_FIELDS = False

    # Prevents the injection of domains into "attrs" if the views already have
    # values in the "attrs" of the target fields.
    # If "False", it overwrites the "attrs" in the rendered view.
    _FAH_XML_INJECT_SAFE = True

    # If this message is sent as an error message in the attr_reg rules,
    # the corresponding check is bypassed.
    _FAH_FORCE_COMMAND = 'no-check'

    # Activates/deactivates the corresponding controls during create()
    _FAH_READONLY_CREATE_CHECK = True
    _FAH_INVISIBLE_CREATE_CHECK = True
    _FAH_REQUIRED_CREATE_CHECK = True
    # Activates/deactivates the corresponding controls during write()
    _FAH_READONLY_WRITE_CHECK = True
    _FAH_REQUIRED_WRITE_CHECK = True
    _FAH_INVISIBLE_WRITE_CHECK = True

    # Displays helper fields in views and makes them non-read-only.
    # Print additional information in the log (debug level).
    _FAH_DEBUG_MODE = False
    # _logger.setLevel(logging.INFO + 1)

    # Marker for error messages in dialogue boxes.
    _FAH_DIALOG_PREFIX = _msg_prefix

    # **==** Start No edit/override **==**
    # @TODO: Maybe it's better and more secure to put it in a more global
    #        place (es. ir.model)
    _GLOBAL_FAH_FIELD_REGISTRY = dict()
    # **==** Stop No edit/override **==**

    #========================================================
    # ** SETUP **
    # Declaration of elements to be overridden.
    # WARNING: If the element does not exist in the view, it does not return
    #          any warning or error! It simply ignores the declaration.
    
    # Declaration of html fields and nodes (elements) whose attributes must point
    # to helper fields.
    # NOTE 1: To assign more than one tag to the same field/node, repeat the declaration
    #         of the field/node by indicating a different tag.
    # NOTE 2: On XML, the single operands in the attrs domains are currently concatenated
    #         exclusively by the OR ('|') operator.
    # - - - - TARGET FIELDS declarations - - - -
    # Model fields and possible tags.
    # es. {'field_name1',('field_name2'), ('field_name2', '#DEMOTAG#')}
    _fah_model_target_fields = set()
    # Comodels' fields linked to the model in dot.notation and optional tags.
    # e.g. {'item1_ids.item1_field', ('item2_ids.item2_field'), ('item3_ids.item3_field', '#DEMOTAG#')}
    _fah_embedded_target_fields = set()
    # Fields that can be modified even if they are readonly and/or invisible.
    # It affects the check on write() and create().
    # NOTE: Model fields only. If you need to force write to a field in a comodel
    #       (embedded field), you must define that field in the "_fah_force_save_fields"
    #       slot of the comodel or manually set the "force_save" attribute in the view
    #       if the comodel does not implement this helper.
    # WARNING: All the target fields of the MODEL will have force_save="1" in the "field"
    #          tag on the XML, no matter if they are declared here or not, because the
    #          write() and create() check already takes care of that; the JS client only
    #          has to send everything to the server, no matter if it is readonly or not
    #          on the view.
    # @todo: What to do with the comodel EMBEDDED fields that do not implement the helper?
    #        At the moment they also have force_save="1" in the <field> tag on the XML.
    #        Turn it off? Make an option to force it or not on embedded fields?
    #        (see todo@models.py)
    _fah_force_save_fields = set()
    # 
    _fah_force_null_fields = set()

    # - - - - OTHER TARGET HTML ELEMENTS declaration - - - -
    # Elements in model views that must have the "invisible" attribute.
    # e.g.. {('group', 'name', 'group-target-1', '#DEMOTAG#')}
    #       It means that the <group> element with name="group-target-1"
    #       must become invisible when the #DEMOTAG# tag appears.
    # NOTE 1: Tested with tags: <group>, <div>, <button>.
    #         For <field> tags use the appropriate slots
    #         "_fah_model_target_fields" or "_fah_embedded_target_fields".
    # NOTE 2: Tested with attributes: id, name
    _fah_model_target_nodes = set()

    # Elements in the embedded views of the model which must have the attributes
    # "invisible" (or "column_invisible" for embedded/inline tree).
    # e.g. {('item_ids', 'button', 'name', 'action_demo', '#HIDE-BUTTON#')}
    _fah_embedded_target_nodes = set()
    # - - - - TRIGGERS declaration - - - -
    # Fields triggering the recomuption of attrs.
    _fah_trigger_fields = set()
    # @todo: ?? Think about whether it may be necessary to allow "embedded" triggers
    #           in dot.notation and especially how the view behaves, if it is
    #           practicable and what side effects it would cause. ??
    #======================================
    # ** SETUP **
    # Compute method for the helper fields
    @api.depends(lambda self: [self._FAH_FIRST_TRIGGER_FIELD, self._FAH_BYPASS_FIELD])
    def _fah_compute_helper_fields(self, attr_reg=False, eval_mode=False, override=False):
        """ Write the content of the "attr_reg" on the helper fields
        :param FahAttrRegistry eval_mode:  Attributes registry. If False, a new empty one will be created.
        :param bool attr_reg:              Whether it is necessary to write on the fields or not.
        :param str override:               Command to handle calls between methods in the MRO chain.
                                           The first external call to the overrided method on real models
                                           must ignore this argument (override==False). It should be for
                                           internal use only. 
        :return:  False
        """
        # WARNING: The _fah_compute_helper_fields() method of this abstract model must
        #          always be executed as the last in the MRO chain. To perform the
        #          write, "eval_mode" must be False and "override" must be False or
        #          "finish".
        attr_reg = attr_reg or FahAttrRegistry(self.env, self._name)

        if self._FAH_DEBUG_MODE:
            log_msg_pre = '_fah_compute_helper_fields %s %s @ %s:\n' % (
                '<EVAL MODE>' if eval_mode else '<compute mode>',
                '[INIT]' if not override else f'[{override}]',
                self._name,
            )
            log_msg_list = ['- '+ attr +': '+ str(attr_reg[attr]) for attr in [*self._FAH_ATTRS, *self._FAH_OPS]]
            _logger.debug(log_msg_pre + '\n'.join(log_msg_list))

        # If override=='compute' it stops here. The entire MRO chain has been ascended.
        # (the "first round" is ended)
        # From now on it will start to compute in the "correct" order until it reaches
        # the last extension/override.
        if override == 'compute':
            return
        
        # Now all computations are done.

        # Add to the attr_reg the attrs declared in fields definitions
        # For all records in the recordset
        for r in self:
            # For all the enabled attrs except 'column_invisible'
            for attr, helper_field_name in self._FAH_ATTRS_TUPLES:
                if attr != 'column_invisible':
                    # For all target fields
                    for target_field in self._FAH_FIELD_REGISTRY['model_target_fields']:
                        # If the field is not in the attr_reg
                        if target_field not in attr_reg[attr].get(r.id, dict()):
                            # If the attr is declared in field definition 
                            if getattr(self._fields[target_field], attr, False):
                                # Add the target field.
                                # If the field is computed or in its definition the argument
                                # "fah_force_save" is passed
                                if getattr(self._fields[target_field], 'compute', False) or \
                                    getattr(self._fields[target_field], 'fah_force_save', False):
                                    # Do not perform the check
                                    attr_reg.set([target_field], attr, True, r, msg=self._FAH_FORCE_COMMAND)
                                else:
                                    attr_reg.set([target_field], attr, True, r)

        # If in "eval_mode" it stops here and writes nothing.
        # NOTE: It is useless trying to return something here, because it seems that the
        #       @api.depends decorator always returns False.
        if eval_mode:
            return

        delimiter = self._FAH_ATTRS_FIELDS_DELIMITER

        # Final writing, to be done only here, in the abstract model.
        for r in self:

            # If the compute option is active at model level and the bypass
            # is not active on this record.
            if self._FAH_HELPER_FIELDS_COMPUTE and not r[self._FAH_BYPASS_FIELD]:
                # For each enabled attr
                for attr, helper_field_name in self._FAH_ATTRS_TUPLES:
                    # Get the values to be written for the attr and the current record.
                    fields_to_attr = attr_reg[attr].get(r.id, dict())
                    # Updates the attribute's helper field.
                    if fields_to_attr:
                        tagged_fields = []
                        for field_name in fields_to_attr:
                            # If not a tag, it adds delimiters to the field name.
                            if field_name[0] != self._FAH_ATTRS_TAG_DELIMITER:
                                tagged_fields.append(delimiter+field_name+delimiter)
                            # If it's a tag, it is written as it is.
                            else:
                                tagged_fields.append(field_name)
                        # Writes the field
                        r[helper_field_name] = json.dumps(tagged_fields)
                    else:
                        r[helper_field_name] = '[]'

                # Only if ops helper fields have been created.
                if self._FAH_CREATE_OPS_FIELDS:
                    # For each enabled op
                    for op, op_field_name, msg_field_name in self._FAH_OPS_TUPLES:
                        # Get the values to be written for the op and the current record.
                        no_op_value = attr_reg[op].get(r.id, (False, '/'))
                        # Updates the op's helper field.
                        r[op_field_name] = no_op_value[0]
                        r[msg_field_name] = no_op_value[1]

            # If the compute option is not active at model level or bypass
            # is active on this record.
            else:
                # For each attr/op write the default value.
                for helper_field_name in self._FAH_ATTRS_FIELDS:
                    r[helper_field_name] = '[]'
                # Only if ops helper fields have been created.
                if self._FAH_CREATE_OPS_FIELDS:
                    for helper_field_name in self._FAH_OPS_FIELDS:
                        r[helper_field_name] = False

                    for helper_field_name in self._FAH_OPS_MSG_FIELDS:
                        r[helper_field_name] = '/'

                # if self._FAH_NO_UNLINK_CHECK:
                #     r[self._FAH_NO_UNLINK_FIELD] = False
                #     r[self._FAH_NO_UNLINK_MSG_FIELD] = '/'


    # Deprecated – Used in v12 when helper fields had to be stored.
    # Forces re-computation of the values of helper fields only on
    # the passed recordset (self).
    # def _action_records_fields_recompute_attrs(self):
    #     helper_fields = self._FAH_ATTRS_FIELDS
    #     for field in helper_fields:
    #         self.env.add_to_compute(self._fields[field], self)
    #     self.recompute()


    # ===================================================================
    # ORM OVERRIDES
    # Check that ATTRS and OPS are complied with.
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        ids = super(FieldAttrsHelper, self)._search(args, offset=offset, limit=limit, order=order,
                                                count=False, access_rights_uid=access_rights_uid)
        if self.env.is_superuser():
            # Rules do not apply in superuser mode
            return len(ids) if count else ids
        
        if not ids:
            return 0 if count else []

        denied_ids = self._check_ops('no_read', self.browse(ids), 'READ', eval_mode=True)
        allowed_ids = [r_id for r_id in ids if r_id not in denied_ids] if denied_ids else ids

        return len(allowed_ids) if count else allowed_ids

    def read(self, fields=None, load='_classic_read'):
        self._check_ops('no_read', self, 'READ')
        return super(FieldAttrsHelper, self).read(fields=fields, load=load)

    def unlink(self):
        self._check_ops('no_unlink', self, 'DELETE')
        return super(FieldAttrsHelper, self).unlink()

    @api.model
    def create(self, values):
        # CODE BEFORE CREATE: SHOULD USE THE 'values' DICT
        new_record = super(FieldAttrsHelper, self).create(values)     
        # CODE AFTER CREATE: CAN USE THE 'new_record' CREATED
        
        attr_reg = FahAttrRegistry(self.env, self._name)
        new_record.sudo()._fah_compute_helper_fields(attr_reg, eval_mode=True)
        
        self._check_ops('no_create', new_record, 'CREATE', attr_reg=attr_reg)
        self._check_fields('create', values, new_record, attr_reg=attr_reg)

        return new_record

    def write(self, values):
        ## < CODE BEFORE WRITE: CAN USE `self`, WITH THE OLD VALUES > ##

        old_values = {field: {r.id: r[field] for r in self} for field in values}

        # We have to execute the write immediately because otherwise it creates the
        # registry on the basis of the original trigger values (from the DB),
        # before the changes (last save).
        res = super(FieldAttrsHelper, self).write(values)
        ## < CODE AFTER WRITE: CAN USE `self`, WITH THE UPDATED VALUES > ##
        
        attr_reg = FahAttrRegistry(self.env, self._name)
        self.sudo()._fah_compute_helper_fields(attr_reg, eval_mode=True)

        self._check_ops('no_write', self, 'WRITE', attr_reg=attr_reg)
        self._check_fields('write', values, self, attr_reg=attr_reg, old_values=old_values)
        
        return res


    # ===================================================================
    # METHOD FOR BYPASS CHECK
    def _check_bypass_user(self):
        for group in self._FAH_BYPASS_GROUPS_ALL:
            if self.env.user.has_group(group):
                break
        else:
            raise UserError(self._usr_msg(
                '''You cannot modify the Bypass field!\n\n\n(FAH)'''))

    # ===================================================================
    # METHOD FOR OPS CHECK
    # NOTE: Optional "attr_reg" is used to allow the _fah_compute_helper_fields()
    #       to be run once and thus reuse the register.
    @api.model
    def _check_ops(self, op, records, ui_op_name, attr_reg=False, eval_mode=False):
        denied_ids = set()
        # Checks are not performed in superuser mode.
        if not self.env.is_superuser():
            # If the op is enabled
            if op in self._FAH_OPS:
                # Get the register
                if not attr_reg:
                    attr_reg = FahAttrRegistry(self.env, self._name)
                    records.sudo()._fah_compute_helper_fields(attr_reg, eval_mode=True)
                for r in records.sudo():
                    if r[self._FAH_BYPASS_FIELD] == True:
                        continue
                    else:
                        # Reads the response
                        no_op_value = attr_reg.get(0, op, r)
                        if no_op_value['val'] == True:
                            if eval_mode == True:
                                denied_ids.add(r.id)
                                continue
                            else:
                                raise UserError(self._usr_msg(
                                    f'''On the record [ {r.display_name} ] having ID [ {r.id} ], the {ui_op_name} operation cannot be performed.{chr(10)}
                                        {no_op_value['msg']}'''))
        return denied_ids if eval_mode else None

    # ===================================================================
    # METHODS FOR ATTRS CHECK
    def _check_fields(self, action, values, records, attr_reg=False, old_values=False):
        # It checks that if the user is writing to the bypass field, he can do so. At the create, the value "False" is always allowed, of course.
        if action == 'create' and values.get(self._FAH_BYPASS_FIELD, False):
            self._check_bypass_user()
        elif action == 'write' and self._FAH_BYPASS_FIELD in values:
            self._check_bypass_user()
        elif action not in ['create', 'write']:
            raise ValueError(_msg_prefix + f''' Model [ {self._name} ] - The argument 'action' passed to the _check_fields() mtehod has an unexpected value: [ {action} ].' ''')

        if not attr_reg:
            attr_reg = FahAttrRegistry(self.env, self._name)
            self.sudo()._fah_compute_helper_fields(attr_reg, eval_mode=True)

        force_save_fields = self._FAH_FIELD_REGISTRY['force_save_fields']
        force_null_fields = self._FAH_FIELD_REGISTRY['force_save_fields']
        for r in records.sudo():
            if r[self._FAH_BYPASS_FIELD] == True:
                pass
            else:
                if action == 'create':
                    if self._FAH_READONLY_CREATE_CHECK:
                        self._check_not_writable_fields(attr_reg, values, r, force_save_fields, 'readonly')
                    if self._FAH_INVISIBLE_CREATE_CHECK:
                        self._check_not_writable_fields(attr_reg, values, r, force_save_fields, 'invisible')
                    if self._FAH_REQUIRED_CREATE_CHECK:
                        self._check_required_fields(attr_reg, r, force_null_fields)
                elif action == 'write':
                    if self._FAH_READONLY_WRITE_CHECK:
                        self._check_not_writable_fields(attr_reg, values, r, force_save_fields, 'readonly', old_values=old_values)
                    if self._FAH_INVISIBLE_WRITE_CHECK:
                        self._check_not_writable_fields(attr_reg, values, r, force_save_fields, 'invisible', old_values=old_values)
                    if self._FAH_REQUIRED_WRITE_CHECK:
                        self._check_required_fields(attr_reg, r, force_null_fields)

    # Method to check whether the 'readonly' or 'invisible' fields have been modified.
    def _check_not_writable_fields(self, attr_reg, values, record, force_save_fields, attr, old_values=False):
        if hasattr(attr_reg, attr):
            if attr not in ['readonly', 'invisible']:
                raise ValueError(_msg_prefix + f''' Model [ {self._name} ] - The argument "attr" passed to the _check_not_writable_fields() method must be "readonly" or "invisible".''')
            not_writable_targets = attr_reg[attr].get(record.id, None)
            if not_writable_targets != None:
                for ro_target in not_writable_targets:
                    custom_err_msg = not_writable_targets[ro_target]
                    # If the message is not the bypass command
                    if custom_err_msg != self._FAH_FORCE_COMMAND:
                        error_on_field = False
                        
                        # If it is in the tag register, it is a tag, so it retrieves the tagged fields.
                        ro_tagged_fields = self._FAH_FIELD_REGISTRY['model_target_field_tags'].get(ro_target, None)
                        if ro_tagged_fields != None:
                            for ro_field in ro_tagged_fields:
                                if (ro_field in values) and (ro_field not in force_save_fields):
                                    error_on_field = ro_field
                        
                        # If it is not in the tag register, it may be a record.
                        elif (ro_target in values) and (ro_target not in force_save_fields):
                            error_on_field = ro_target
                        
                        # If there are problems and there are also old_values (from the write).
                        if error_on_field and old_values:
                            # Check if the two values are identical because in that case it should not block.
                            # NOTE: Useful e.g. in case of direct write() or calendar view.
                            if old_values[error_on_field][record.id] == record[error_on_field]:
                                error_on_field = False
                        # Otherwise, if there are problems but no old_values (from create).
                        elif error_on_field and not old_values:
                            # Check if the value corresponds to the default value because in that case
                            # it should not block.
                            default_value = record.default_get([error_on_field]).get(error_on_field, None)
                            if default_value == None:
                                if not record[error_on_field]:
                                    error_on_field = False
                            else:
                                if default_value == record[error_on_field]:
                                    error_on_field = False

                        if error_on_field:
                            custom_err_msg = 'Info: '+ custom_err_msg if custom_err_msg else ''
                            ui_attr_name = 'READ-ONLY' if attr == 'readonly' else 'currently NOT VISIBLE'
                            raise ValidationError(self._usr_msg(
                                f'''OPERATION ABORTED!
                                    Model: {self._description} ({self._name})
                                    Record: {record.display_name} ({record.id}){chr(10)}
                                    The field [ {self._fields[error_on_field].string} ] is {ui_attr_name}!
                                    You cannot write on this field.
                                    {chr(160)}
                                    {custom_err_msg}
                                    {chr(160)}
                                    ({error_on_field}{(', '+ro_target) if ro_target[0] == self._FAH_ATTRS_TAG_DELIMITER else ''})'''
                            ))


    # Method to check whether the 'required' fields are actually filled in.
    def _check_required_fields(self, attr_reg, record, force_null_fields):
        if hasattr(attr_reg, 'required'):
            required_targets = attr_reg.required.get(record.id, None)
            if required_targets != None:
                for req_target in required_targets:
                    custom_err_msg = required_targets[req_target]
                    # If the message is not the bypass command.
                    if custom_err_msg != self._FAH_FORCE_COMMAND:
                        
                        # If it is in the tag register, it is a tag, so it retrieves the tagged fields.
                        req_tagged_fields = self._FAH_FIELD_REGISTRY['model_target_field_tags'].get(req_target, None)
                        if req_tagged_fields != None:
                            for req_field in req_tagged_fields:
                                if req_field not in force_null_fields:
                                    self._check_null_required_field(record, req_field, custom_err_msg, tag=req_target)
                    
                        # If it is not in the tag register, it could be a record.
                        elif req_target not in force_null_fields:
                            self._check_null_required_field(record, req_target, custom_err_msg)

    def _check_null_required_field(self, record, field_name, custom_err_msg, tag=False):
        all_right = False
        field_type = self._fields.get(field_name).type
        if field_type == 'boolean':
            return
        elif field_type in ['integer', 'float', 'monetary']:
            # NOTE IN PYTHON: False == 0 and False is not 0
            all_right = record[field_name] != False
            # all_right = record[field_name] is not False
        elif field_type in ['selection', 'date', 'datetime']:
            all_right = record[field_name] != False
        elif field_type in ['char', 'text']:
            if record[field_name] != False:
                all_right = record[field_name].strip() != ''
        elif field_type == 'html':
            html2text = html.document_fromstring(record[field_name]).text_content()
            all_right = html2text.strip() != ''
        elif field_type in ['many2one', 'one2many', 'many2many']:
            all_right = len(record[field_name]) > 0
        else:
            raise ValidationError(self._dev_msg('Not implemented field type: ' + field_type))

        if not all_right:
            custom_err_msg = 'Info: '+ custom_err_msg if custom_err_msg else ''
            raise ValidationError(self._usr_msg(
                f'''OPERATION ABORTED!
                    Model: {self._description} ({self._name})
                    Record: {record.display_name} ({record.id}){chr(10)}
                    The field [ {self._fields[field_name].string} ] is REQUIRED!
                    You must fill in this field.
                    {chr(160)}
                    {custom_err_msg}
                    {chr(160)}
                    ({field_name}{(', '+tag) if tag else ''})'''
            ))


    # ===================================================================
    # METHODS FOR READING THE TRIGGERS/TARGETS DECLARATION SLOTS
    # Methods to retrieve the complete list of target/trigger and node target
    # fields defined in the various real models that inherit this class.
    # We go up the hierarchy of inherited classes (with self.__class__.__bases__)
    # to get the various values, because the attribute is supposed to be overridden
    # by the last instance of the class doing the inheriting.
    # NOTE: These methods are currently only used by _setup_complete().
    # 
    # @todo: The cheks performed in here are almost all the same, but still have
    #        small differences in error messages. Be aware that there is a lot of
    #        duplicate code and that we should group all controls of the same
    #        type under one method and then call that method.

    @api.model
    def _fah_get_trigger_fields(self):
        def_slot = '_fah_trigger_fields'
        if self._FAH_DEBUG_MODE:
            _logger.debug('Get TRIGGER fields from: ' + str(self.__class__.__bases__))
        trigger_fields = set()
        for model in self.__class__.__bases__:
            if hasattr(model, def_slot):
                trigger_fields.update(getattr(model, def_slot))

        for field_name in trigger_fields:
            # If it's not a string
            if type(field_name) != str:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                        The declaration of a trigger must be of 'str' type!'''))

            # If it does not contain a dot
            if '.' not in field_name:
                # If the field don't exist
                if not hasattr(self.env[self._name], field_name):
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                            The Field [ {field_name} ] does not exist in the model [ {self._name} ].'''))
            # If it contains a dot
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                        Dot.notation fields are not allowed in triggers.'''))
            
            # If it's in the blacklist
            if field_name in self._FAH_BLACKLIST_CORE_FIELDS:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                        It is not possible to declare the field [ {field_name} ] as a TRIGGER because it is a helper field in the model [ {self._name} ].'''))

        return trigger_fields
    

    @api.model
    def _fah_get_model_target_fields_and_tags(self):
        def_slot = '_fah_model_target_fields'
        if self._FAH_DEBUG_MODE:
            _logger.debug('Get MODEL TARGET fields from: ' + str(self.__class__.__bases__))
        target_fields = set()
        for model in self.__class__.__bases__:
            if hasattr(model, def_slot):
                target_fields.update(getattr(model, def_slot))
        
        target_fields_dict = dict()
        target_tags_dict = dict()
        for field_def in target_fields:
            # CHECKING THE EXISTENCE OF THE DEFINED TARGET FIELD IN THE MODEL
            tag = False
            if type(field_def) == str:
                field_name = field_def
            elif type(field_def) == tuple:
                if len(field_def) == 1:
                    field_name = field_def[0]
                elif len(field_def) == 2:
                    field_name, tag = field_def
                else:
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                            Wrong tuple length!'''))
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                        The declaration of a target field must be of 'str' or 'tuple' type!'''))

            # If it does not contain a dot
            if '.' not in field_name:
                # If the field don't exist
                if not hasattr(self.env[self._name], field_name):
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                            The Field [ {field_name} ] does not exist in the model [ {self._name} ].'''))
            # If it contains a dot
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                        A MODEL target field must be in simple format/notation (no dot): e.g. field_name'''))
            
            # If it's in the blacklist
            if field_name in self._FAH_BLACKLIST_CORE_FIELDS:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                        It is not possible to declare the field [ {field_name} ] as a TARGET because it is a helper field in the model [ {self._name} ].'''))

            # COMPILING DICT:SET WITH DEFINED EMBEDDED TARGET FIELDS
            # Creates the key with the field name if don't exist.
            if type(target_fields_dict.get(field_name, False)) != set:
                target_fields_dict[field_name] = set()
            if tag:
                if tag[0] != self._FAH_ATTRS_TAG_DELIMITER:
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                            The first character of a Tag must be "{self._FAH_ATTRS_TAG_DELIMITER}".'''))
                # Adds the tag to the set inside the field_name
                target_fields_dict[field_name].add(tag)

                # Creates the key with the tag name if don't exist.
                if type(target_tags_dict.get(tag, False)) != set:
                    target_tags_dict[tag] = set()
                # Adds the field_name to the set inside the tag.
                target_tags_dict[tag].add(field_name)

        return (target_fields_dict, target_tags_dict)

    @api.model
    def _fah_get_embedded_target_fields(self):
        def_slot = '_fah_embedded_target_fields'
        if self._FAH_DEBUG_MODE:
            _logger.debug('Get EMBEDDED TARGET fields from: ' + str(self.__class__.__bases__))
        target_fields = set()
        for model in self.__class__.__bases__:
            if hasattr(model, def_slot):
                target_fields.update(getattr(model, def_slot))
        target_fields_dict = dict()
        for field_def in target_fields:

            tag = False
            if type(field_def) == str:
                field_name = field_def
            elif type(field_def) == tuple:
                if len(field_def) == 1:
                    field_name = field_def[0]
                elif len(field_def) == 2:
                    field_name, tag = field_def
                else:
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                            Wrong tuple length!'''))
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                        The declaration of a target field must be of 'str' or 'tuple' type!'''))


            nested_field_name_list = field_name.split('.')
            
            if len(nested_field_name_list) != 2:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]:{chr(10)}
                        An EMBEDDED target field must be in dot.notation: e.g. item_ids.item_field'''))
            
            parent_field_name, child_field_name = nested_field_name_list
            
            # CHECKING THE EXISTENCE OF DEFINED TARGET FIELDS IN THE COMODEL
            # If the field exists
            if hasattr(self, parent_field_name):
                RelModel = self.env[self[parent_field_name]._name]
                # If the field is o2m or m2m
                if self._fields.get(parent_field_name).type in ['one2many', 'many2many']:
                    if child_field_name in RelModel._fields:
                        if isinstance(RelModel, FieldAttrsHelper):
                            # If it's in the blacklist
                            if child_field_name in RelModel._FAH_BLACKLIST_CORE_FIELDS:
                                raise UserError(self._dev_msg(
                                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                                        It is not possible to declare the field [ {child_field_name} ] as a TARGET because it is a helper field in the model [ {RelModel._name} ].'''))
                            else: pass
                        else: pass
                    else:
                        raise UserError(self._dev_msg(
                            f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]:{chr(10)}
                                Through the field [ {parent_field_name} ] you are trying to manage the attributes of the field [ {child_field_name} ] which is not a field of the model [ {RelModel._name} ].'''))
                else:
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]:{chr(10)}
                            [ {parent_field_name} ] is not a relational field of type One2many or Many2many.'''))
            # If the field doesn't exist
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]:{chr(10)}
                        The Field [ {parent_field_name} ] does not exist in the model [ {self._name} ]'''))

            # COMPILING DICT:SET WITH DEFINED EMBEDDED TARGET FIELDS
            # If keys don't yet exist, create them
            if not target_fields_dict.get(parent_field_name, False):
                target_fields_dict[parent_field_name] = dict()
            if type(target_fields_dict[parent_field_name].get(child_field_name, False)) != set:
                target_fields_dict[parent_field_name][child_field_name] = set()
            # If there is the tag, it adds it
            if tag:
                if tag[0] != self._FAH_ATTRS_TAG_DELIMITER:
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_def} ]{chr(10)}:
                            The first character of a Tag must be "{self._FAH_ATTRS_TAG_DELIMITER}".'''))
                # Adds the tag to the set inside the node
                target_fields_dict[parent_field_name][child_field_name].add(tag)

        return target_fields_dict

    @api.model
    def _fah_get_model_target_nodes(self):
        def_slot = '_fah_model_target_nodes'
        if self._FAH_DEBUG_MODE:
            _logger.debug('Get MODEL TARGET NODES from: ' + str(self.__class__.__bases__))
        target_nodes = set()
        for model in self.__class__.__bases__:
            if hasattr(model, def_slot):
                target_nodes.update(getattr(model, def_slot))
        
        target_nodes_dict = dict()
        for node_def in target_nodes:
            if type(node_def) != tuple:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]{chr(10)}:
                        The declaration of a target node must be of 'tuple' type!'''))
            if len(node_def) != 4:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]{chr(10)}:
                        Tuples within '_fah_model_target_nodes' must have 4 elements.'''))

            htmltag, attr, value, tag = node_def
            
            if tag[0] != self._FAH_ATTRS_TAG_DELIMITER:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]{chr(10)}:
                        The first character of a Tag must be "{self._FAH_ATTRS_TAG_DELIMITER}".'''))

            if htmltag == 'field':
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]:{chr(10)}
                        You are trying to manage the attributes of a field (<field> html tag) but targets of type "field" must be inserted in the appropriate slot "_fah_model_target_fields" or "_fah_embedded_target_fields".'''))

            # COMPILING DICT:SET WITH DEFINED TARGET NODES
            # If the key with the name of the relational field does not exist, creates it.
            if not target_nodes_dict.get((htmltag, attr, value), False):
                target_nodes_dict[(htmltag, attr, value)] = set()
            
            # Adds the tag to the set inside the node
            target_nodes_dict[(htmltag, attr, value)].add(tag)

        return target_nodes_dict

    @api.model
    def _fah_get_embedded_target_nodes(self):
        def_slot = '_fah_embedded_target_nodes'
        if self._FAH_DEBUG_MODE:
            _logger.debug('Get EMBEDDED TARGET NODES from: ' + str(self.__class__.__bases__))
        target_nodes = set()
        for model in self.__class__.__bases__:
            if hasattr(model, def_slot):
                target_nodes.update(getattr(model, def_slot))

        target_nodes_dict = dict()
        for node_def in target_nodes:
            if len(node_def) != 5:
                raise UserError(self._dev_msg(
                    f'''Tuples within "{def_slot}" must have 5 elements.:
                        {node_def}'''))
            
            parent_field_name, htmltag, attr, value, tag = node_def
            
            if tag[0] != self._FAH_ATTRS_TAG_DELIMITER:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]{chr(10)}:
                        The first character of a Tag must be "{self._FAH_ATTRS_TAG_DELIMITER}".'''))

            # if htmltag == 'field':
            #     raise UserError(self._dev_msg(
            #         f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]:{chr(10)}
            #             You are trying to manage the attributes of a field (<field> html tag) but targets of type "field" must be inserted in the appropriate slot "_fah_model_target_fields".'''))

            # NODE DECLARATION CHECK
            # If the field exists
            if hasattr(self, parent_field_name):
                # If the field is o2m or m2m
                if self._fields.get(parent_field_name).type in ['one2many', 'many2many']:
                    if htmltag == 'field':
                        raise UserError(self._dev_msg(
                            f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]:{chr(10)}
                                Through the field [ {parent_field_name} ] you are trying to manage the attributes of a field (field html tag) but embedded fields must be inserted in the appropriate slot "_fah_embedded_target_fields".'''))
                else:
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]:{chr(10)}
                            [ {parent_field_name} ] is not a relational field of type One2many or Many2many.'''))
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {node_def} ]:{chr(10)}
                        The Field [ {parent_field_name} ] does not exist in the model [ {self._name} ]'''))

            # COMPILING DICT:SET WITH DEFINED EMBEDDED TARGET FIELDS
            # If the key with the name of the relational field does not exist, it creates it.
            if not target_nodes_dict.get(parent_field_name, False):
                target_nodes_dict[parent_field_name] = dict()
            
            # If inside the key with the relational field name there is no key for the
            # current node, it creates it.
            if not target_nodes_dict[parent_field_name].get((htmltag, attr, value), False):
                target_nodes_dict[parent_field_name][(htmltag, attr, value)] = set()
            
            # Adds the tag to the set inside the node
            target_nodes_dict[parent_field_name][(htmltag, attr, value)].add(tag)

        return target_nodes_dict

    @api.model
    def _fah_get_force_save_fields(self):
        return self._fah_get_force_fields('_fah_force_save_fields')

    @api.model
    def _fah_get_force_null_fields(self):
        return self._fah_get_force_fields('_fah_force_null_fields')

    @api.model
    def _fah_get_force_fields(self, def_slot):
        if self._FAH_DEBUG_MODE:
            _logger.debug(f'Get {def_slot} from: ' + str(self.__class__.__bases__))
        force_fields = set()
        for model in self.__class__.__bases__:
            if hasattr(model, def_slot):
                force_fields.update(getattr(model, def_slot))
        
        for field_name in force_fields:
            # If it's not a string
            if type(field_name) != str:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                        The declaration of a {def_slot} must be of 'str' type!'''))

            # If it does not contain a dot
            if '.' not in field_name:
                # If the field doesn't exist
                if not hasattr(self.env[self._name], field_name):
                    raise UserError(self._dev_msg(
                        f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                            The Field [ {field_name} ] does not exist in the model [ {self._name} ].'''))
            # If it contains a dot
            else:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                        Dot.notation fields are not allowed in the {def_slot}.'''))
            
            # If it's in the blacklist
            if field_name in self._FAH_BLACKLIST_CORE_FIELDS:
                raise UserError(self._dev_msg(
                    f'''- MODEL [ {self._name} ]{chr(10)}- DECLARATION OF [ {def_slot} ]{chr(10)}- ELEM. [ {field_name} ]{chr(10)}:
                        It is not possible to force the field [ {field_name} ] as it is a helper field in the model [ {self._name} ].'''))

        return force_fields


    # ===================================================
    # METHODS FOR FORMATTING ERROR MESSAGES FOR DEVELOPMENT
    # OR USER ASSISTANCE PURPOSES
    # The idea is that messages for developers should no longer appear
    # in production. If this happens it means that there has been some
    # development or typing error.
    # This is why there are two different types of messages.

    # Messages for the developer
    @api.model
    def _dev_msg(self, msg):
        return self._FAH_DIALOG_PREFIX +'\n'+ dedent(msg)+'\n\n\n'+\
            'PLEASE CONTACT A SYSTEM ADMINISTRATOR AND REPORT THE TEXT OF THIS ERROR.\n'+ \
            'THANK YOU.'

    # Messages for the user
    @api.model
    def _usr_msg(self, msg):
        return dedent(msg)
