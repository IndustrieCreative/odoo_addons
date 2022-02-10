# -*- coding: utf-8 -*-

import logging
from odoo import api
from . attr_registry import FahAttrRegistry
from . models.web_fieldattrs_helper import FieldAttrsHelper, _msg_prefix

_logger = logging.getLogger(__name__+' | '+_msg_prefix +' :\n')

# Decorator
def fah_depends(*args):
    def wrapper_fn(func):

        @api.depends(*args)
        def inner_fn(self, attr_reg=False, eval_mode=False, override=False):
            # Checking that the method has inherited the abstract model of the helper
            if isinstance(self, FieldAttrsHelper):
                attr_reg = attr_reg or FahAttrRegistry(self.env, self._name)
                func(self, attr_reg, eval_mode=eval_mode, override=override)
            else:
                raise TypeError('''To use the @fah_depends decorator, the model to which the method belongs must have inherited the abstract model "web.fieldattrs.helper" by adding it to its "_inherit" attribute.''')

        return inner_fn
    return wrapper_fn

# I register the new decorator in the core api to save a line in the imports.
api.fah_depends = fah_depends
