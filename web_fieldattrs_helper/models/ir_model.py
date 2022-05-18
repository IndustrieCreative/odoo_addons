# -*- coding: utf-8 -*-

# import inspect
from pprint import pformat
from odoo import fields, models
from . web_fieldattrs_helper import FieldAttrsHelper

# Override for the sole purpose of displaying the implementation status of the helper
# on each model in the UI, at runtime.
class IrModel(models.Model):
    _inherit = 'ir.model'

    fah_implemented = fields.Boolean(
        compute = '_compute_fah_implemented',
        search = '_search_fah_implemented',
        string = 'FAH active?',
        store = False,
        help = '''"True" if this model implements FAH in its Python class definition.'''
    )

    fah_model_status = fields.Text(
        string = 'FAH Status on this model',
        compute = '_compute_fah_status',
        store = False
    )

    def _compute_fah_implemented(self):
        for r in self:
            r.fah_implemented = False
            if self.env.get(r.model) is not None:
                if isinstance(self.env[r.model], FieldAttrsHelper):
                    r.fah_implemented = True

    def _search_fah_implemented(self, operator, value):
        active_model_ids = []
        for model in self.search([]):
            if self.env.get(model.model) is not None:
                if isinstance(self.env[model.model], FieldAttrsHelper):
                    active_model_ids.append(model.id)
        # Bypass search operator
        if operator == '=':
            return [('id', 'in', active_model_ids)]
        elif operator == '!=':
            return [('id', 'not in', active_model_ids)]

    def _compute_fah_status(self):
        for r in self:
            if self.env.get(r.model) is not None:
                Model = self.env[r.model]
                if isinstance(Model, FieldAttrsHelper):
                    r.fah_model_status = f'''
# MODEL:
{Model._name}
-------------------
# SETTINGS:
_FAH_ATTRS = {pformat(Model._FAH_ATTRS)}
_FAH_OPS = {pformat(Model._FAH_OPS)}
_FAH_FIELDS_PREFIX = {pformat(Model._FAH_FIELDS_PREFIX)}
_FAH_ATTRS_FIELDS_DELIMITER = {pformat(Model._FAH_ATTRS_FIELDS_DELIMITER)}
_FAH_ATTRS_TAG_DELIMITER = {pformat(Model._FAH_ATTRS_TAG_DELIMITER)}
_FAH_FORCE_COMMAND = {pformat(Model._FAH_FORCE_COMMAND)}
_FAH_BYPASS_GROUPS_ADD = {pformat(Model._FAH_BYPASS_GROUPS_ADD)}
_FAH_BYPASS_CORE_GROUP = {pformat(Model._FAH_BYPASS_CORE_GROUP)} # **!! DO NOT OVERRIDE !!**
_FAH_HELPER_FIELDS_COMPUTE = {pformat(Model._FAH_HELPER_FIELDS_COMPUTE)}
_FAH_XML_INJECT = {pformat(Model._FAH_XML_INJECT)}
_FAH_XML_INJECT_ATTRS = {pformat(Model._FAH_XML_INJECT_ATTRS)}
_FAH_XML_INJECT_SAFE = {pformat(Model._FAH_XML_INJECT_SAFE)}
_FAH_CREATE_OPS_FIELDS = {pformat(Model._FAH_CREATE_OPS_FIELDS)}
_FAH_READONLY_CREATE_CHECK = {pformat(Model._FAH_READONLY_CREATE_CHECK)}
_FAH_INVISIBLE_CREATE_CHECK = {pformat(Model._FAH_INVISIBLE_CREATE_CHECK)}
_FAH_REQUIRED_CREATE_CHECK = {pformat(Model._FAH_REQUIRED_CREATE_CHECK)}
_FAH_READONLY_WRITE_CHECK = {pformat(Model._FAH_READONLY_WRITE_CHECK)}
_FAH_REQUIRED_WRITE_CHECK = {pformat(Model._FAH_REQUIRED_WRITE_CHECK)}
_FAH_INVISIBLE_WRITE_CHECK = {pformat(Model._FAH_INVISIBLE_WRITE_CHECK)}
_FAH_DEBUG_MODE = {pformat(Model._FAH_DEBUG_MODE)}
_FAH_DIALOG_PREFIX = {pformat(Model._FAH_DIALOG_PREFIX)}


-------------------
# SELF-GENERETED SETTINGS **!! DO NOT OVERRIDE !!**
_FAH_ATTRS_FIELDS = {Model._FAH_ATTRS_FIELDS}
_FAH_OPS_FIELDS = {Model._FAH_OPS_FIELDS}
_FAH_OPS_MSG_FIELDS = {Model._FAH_OPS_MSG_FIELDS}
_FAH_BYPASS_FIELD = {pformat(Model._FAH_BYPASS_FIELD)}
_FAH_BYPASS_GROUPS_ALL = {pformat(Model._FAH_BYPASS_GROUPS_ALL)}
_FAH_BLACKLIST_CORE_FIELDS = {Model._FAH_BLACKLIST_CORE_FIELDS}
_FAH_STARTER_FIELD = {pformat(Model._FAH_STARTER_FIELD)}
_FAH_FIRST_TRIGGER_FIELD = {pformat(Model._FAH_FIRST_TRIGGER_FIELD)}
-------------------
# Model's triggered methods:
_fah_compute_helper_fields._depends = {Model._fah_compute_helper_fields._depends}
_fah_onchange_starter_field._onchange = {Model._fah_onchange_starter_field._onchange}
-------------------
# Model's class inheritance:
{str(Model.__class__.__bases__)}
-------------------
_FAH_FIELD_REGISTRY =          # **!! DO NOT OVERRIDE !!**
{pformat(Model._FAH_FIELD_REGISTRY)}
                '''
                else:
                    r.fah_model_status = f'FAH NOT IMPLEMENTED ON MODEL {Model._name}'
            else:
                r.fah_model_status = f'FAH: MODEL {Model._name} NOT FOUND ON THE ENVIRONMENT.'

# -------------------
# METHOD _fah_compute_helper_fields()
# {inspect.getsource(Model._fah_compute_helper_fields)}
