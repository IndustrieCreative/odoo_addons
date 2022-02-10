# -*- coding: utf-8 -*-

# @todo: use "collections" to simplify the code

import logging
from odoo import models
from odoo.exceptions import ValidationError

# Marker for messages in logs and default for dialogue boxes.
_msg_prefix = '** WEB FIELD ATTRS HELPER **'
_logger = logging.getLogger(__name__+' | '+_msg_prefix +' :\n')

# Class for creating registers of nuclear actions performed by the
# "compute" function (_fah_compute_helper_fields)
class FahAttrRegistry:
    def __init__(self, env, model_name):
        Model = env[model_name]
        #  Create a property for each attribute
        for attr in [*Model._FAH_ATTRS, *Model._FAH_OPS]:
            setattr(self, attr, dict())
        # The model that created the instance
        self.model = Model
        # Gets the dict with the target fields of the model
        self.model_target_fields = Model._FAH_FIELD_REGISTRY['model_target_fields']
        # Gets the dict with embedded fields (towards comodels)
        self.embedded_target_fields = Model._FAH_FIELD_REGISTRY['embedded_target_fields']
        # @todo: ?? add nodes + tag definition controls during FahAttrRegistry.set()
        if Model._FAH_DEBUG_MODE:
            _logger.debug('Create FahAttrRegistry from class: ' + str(Model.__class__))
            _logger.debug('Create FahAttrRegistry - model target fields found: ' + str(self.model_target_fields))
            _logger.debug('Create FahAttrRegistry - embedded target fields found: ' + str(self.embedded_target_fields))
    
    # Makes the object subscriptable
    def __getitem__(self, item):
         return getattr(self, item)
    
    # Method for setting the attr/op of one or more field/tags on a given record
    # NOTE: When using tags, only the "invisible" attr will be set on nodes (xml elements except
    #       fields). In the case of embedded nodes, also the attr "column_invisible".
    #       All other attr will be ignored (as meaningless).
    def set(self, target_names, attr, value, record, msg=False):
        """ Set a boolean value to an attr on specific target names of a record.
        :param list target_names:  list of strings containing the names of the targets (fields or tags)
        :param str attr:           the attribute; available values are the attrs ('readonly', 'required', 'invisible', 'column_invisible')
                                   or the ops ('no_read', 'no_write', 'no_create', 'no_unlink')
        :param bool value:         the value to be set
        :param record:             the record (must be a record of the model that created the registry object)
        :param str msg:            optional message for the user, if this rule is supposed to raise an error during write, create, unlink or read.
        """  
        # If it is an "attr"
        if attr in self.model._FAH_ATTRS:

            # ------------
            # VALUE checks
            if value == False and msg:
                raise ValidationError(self.model._dev_msg(
                    f'''FahAttrRegistry.set(): {target_names} | {attr} | {value} | {record.id}:{chr(10)}
                        The argument "msg" is not allowed if the "value" is not True!'''))
            if type(value) != bool:
                raise ValidationError(self.model._dev_msg(
                    f'''FahAttrRegistry.set(): {target_names} | {attr} | {value} | {record.id}:{chr(10)}
                        The argument "value" must be boolean!'''))

            # -------------
            # RECORD check
            self._record_check(record)

            # Foe each target_names
            for target_name in target_names:
                # ------------------
                # TARGET_NAMES CHECKS

                # CHECK IF IT IS A FIELD OR A TAG
                # If it is a tag
                if target_name[0] == self.model._FAH_ATTRS_TAG_DELIMITER:
                    pass
                    # @todo: ?? Check that the tag is used by some element. ??
                # If it is not a tag, it should be a field
                else:
                    # CHECKING THE EXISTENCE OF THE FIELD PASSED IN THE TARGET FIELD DEFINITION
                    # If it contains a dot, it is an embedded field (relational)
                    if '.' in target_name:
                        # Split the field name
                        nested_field_name_list = target_name.split('.')
                        if len(nested_field_name_list) != 2:
                            raise ValidationError(self.model._dev_msg(
                                f'''FahAttrRegistry.set(): {target_names} | {attr} | {value} | {record.id}:{chr(10)}
                                    The nested field must be in dot.notation: es. item_ids.item_field'''))
                        parent_field_name, child_field_name = nested_field_name_list

                        # Check that the field name is among the target embedded field names,
                        # otherwise it raises an error.
                        intruder = False
                        if parent_field_name not in self.embedded_target_fields:
                            intruder = True
                        else:
                            if child_field_name not in self.embedded_target_fields[parent_field_name]:
                                intruder = True
                        if intruder:    
                            raise ValidationError(self.model._dev_msg(
                                f'''FahAttrRegistry.set(): {target_names} | {attr} | {value} | {record.id}:{chr(10)}
                                    You are trying to modify (on the view) an attribute of the field [ {target_name} ] that is not defined in the "_fah_embedded_target_fields" property of the model [ {self.model._name} ].'''))
                    # If it does not contain a point, it is a model field.
                    else:
                        # Check that the field name is among the model target field names,
                        # otherwise it raises an error.
                        if target_name not in self.model_target_fields:
                            raise ValidationError(self.model._dev_msg(
                                f'''FahAttrRegistry.set(): {target_names} | {attr} | {value} | {record.id}:{chr(10)}
                                   You are trying to modify (on the view) an attribute of the field [ {target_name} ] that is not defined in the "_fah_model_target_fields" property of the model [ {self.model._name} ].'''))
            # ------------------
            # TARGET_NAMES SET

            # For the current attr, it get the dict whose keys are the IDs of the records.
            # NOTE: Each ID contains (for that specific record) the fields currently to
            #       be affected by the attribute.
            # For the current record, it obtains the set with the current fields within the attribute.
            # If there is no key for the current ID
            if self[attr].get(record.id, None) == None:
                # Creates the key with the current ID
                self[attr].update({record.id: dict()})
            # Finally, it adds or removes fields depending on the value to be taken by the attribute
            if value == True:
                self[attr][record.id].update({fname: msg for fname in target_names})
            else:
                for fname in target_names:
                    if fname in self[attr][record.id]:
                        del self[attr][record.id][fname]
        # If it is an "op"
        elif attr in self.model._FAH_OPS:
            if value == True:
                # Creates the key with the current ID
                self[attr].update({record.id: (value, msg)})
            else:
                if record.id in self[attr]:
                    del self[attr][record.id]
        else:
            raise ValidationError(self.model._dev_msg(
                f'''FahAttrRegistry.set(): {target_names} | {attr} | {value} | {record.id}:{chr(10)}
                    Unknown attribute: [ {attr} ]
                    The argument "attr" passed to the FahAttrRegistry.set() method has an unexpected value.
                    The allowed values are: {', '.join([*self.model._FAH_ATTRS, *self.model._FAH_OPS])}.'''))

    # Method to get the current attr value of a field/tag of a given record.
    def get(self, target_name, attr, record):
        """ Get the current value of an attr of a specific target name and record.
        :param str target_name:  the name of a field or tag
        :param str attr:         the attribute; available values are the attrs ('readonly', 'required', 'invisible', 'column_invisible')
                                 or the ops ('no_read', 'no_write', 'no_create', 'no_unlink')
        :param record:           the record (must be a record of the model that created the registry object)
        :return:                 dict containing the keys 'val' (bool) and 'msg' (str)
        :rtype:                  dict
        """
        # -------------
        # RECORD check
        self._record_check(record)
        
        # NOTE: When reading, we do not make any other checks.
        #       If something does not exist, it just returns "False".
        if hasattr(self, attr):
            if record.id in self[attr]:
                if attr in self.model._FAH_ATTRS:
                    if target_name in self[attr][record.id]:
                        return {'val': True, 'msg': self[attr][record.id][target_name]}
                elif attr in self.model._FAH_OPS:
                    return {'val': True, 'msg': self[attr][record.id][1]}
            # NOTE: If a field or tag is not present in the attr_reg,
            #       then the value of the attribute is definitely "False".
            return {'val': False, 'msg': False}

    # Method for checking records passed to the set() and get() methods.
    def _record_check(self, record):
        # Must be a recordset
        if not isinstance(record, models.BaseModel):
            raise ValidationError(self.model._dev_msg(
                '''FahAttrRegistry.set(): The "record" argument must be a recorset.'''))
        # Must be a singleton
        if len(record) != 1:
            raise ValidationError(self.model._dev_msg(
                '''FahAttrRegistry.set(): The "record" argument must be a recorset.'''))
        # Must be of the same model
        if record._name != self.model._name:
            raise ValidationError(self.model._dev_msg(
                f'''FahAttrRegistry.set(): The passed record ({record._name}) must be of the same current model ({self.model._name}).'''))
