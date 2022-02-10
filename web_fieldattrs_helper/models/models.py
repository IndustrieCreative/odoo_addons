# -*- coding: utf-8 -*-
from lxml import etree
from odoo import api, models
from odoo.exceptions import UserError
from . web_fieldattrs_helper import FieldAttrsHelper

# Override for the purpose of automatically injecting attrs into XML elements
# declared as targets.
# NOTE: We override _fields_view_get() directly on the BaseModel so it is always executed,
#       even on models that do not implement the helper. This way, it is always possible
#       to inject attrs into embedded/inline view fields pointing to comodels that
#       implement this helper, even if the main model does not implement it.
class Base(models.AbstractModel):
    _inherit = 'base'

    # Injects helper fields and "attrs" into the views.
    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Base, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        
        doc = etree.XML(res['arch'])

        if 'view_id' in res:
            current_view_id = res['view_id']
        else:
            current_view_id = False

        #---------------------------------------------------------
        # HELPER FIELDS
        #---------------------------------------------------------
        
        # NOTE: First we inject the helper fields and then the attrs.
        #     I'm repeating all the "view_type" conditions because, for now,
        #     I prefer to keep field-injections separate from attrs-injections.

        if view_type == 'form':
            # - - - - - - -
            # MODEL FIELDS
            if isinstance(self, FieldAttrsHelper):
                if self._FAH_XML_INJECT:
                    # If a <sheet> node exists, use that, otherwise use the <form>
                    sheet_nodes = doc.xpath("//sheet[not (ancestor::field)]")
                    if len(sheet_nodes) > 0:
                        main_nodes = sheet_nodes
                    else:
                        main_nodes = doc.xpath("//form[not (ancestor::field)]")

                    for main_node in main_nodes:
                        # From Debug mode
                        if self._FAH_DEBUG_MODE:
                            xml_group = etree.Element('group', {
                                'string': 'Attrs Helper Fields (debug mode active!)',
                                'name': 'fah_debug_group',
                                'invisible': '0',
                                'readonly': '0',
                                'class': 'asc_label_nowrap',
                            })
                            # ATTRS
                            for hf_name in self._FAH_ATTRS_FIELDS:
                                xml_field = etree.Element('field', {
                                    'name': hf_name, 
                                    'invisible': '0',
                                    'readonly': '0',
                                })
                                xml_group.append(xml_field)
                            # OPS
                            if self._FAH_CREATE_OPS_FIELDS:
                                for hf_name in [*self._FAH_OPS_FIELDS, *self._FAH_OPS_MSG_FIELDS]:
                                    xml_field = etree.Element('field', {
                                        'name': hf_name, 
                                        'invisible': '0',
                                        'readonly': '0',
                                    })
                                    xml_group.append(xml_field)
                            # BYPASS
                            xml_group.append(etree.Element('field', {
                                'name': self._FAH_BYPASS_FIELD, 
                                'groups': ','.join(self._FAH_BYPASS_GROUPS_ALL),
                            }))
                            main_node.append(xml_group)
                        # Form normal mode
                        else:
                            # ATTRS
                            for hf_name in self._FAH_ATTRS_FIELDS:
                                xml_field = etree.Element('field', {
                                    'name': hf_name,
                                    'invisible': '1',
                                    'readonly': '1',
                                })
                                main_node.append(xml_field)
                            # OPS
                            if self._FAH_CREATE_OPS_FIELDS:
                                for hf_name in [*self._FAH_OPS_FIELDS, *self._FAH_OPS_MSG_FIELDS]:
                                    xml_field = etree.Element('field', {
                                        'name': hf_name,
                                        'invisible': '1',
                                        'readonly': '1',
                                    })
                                    main_node.append(xml_field)
                            # BYPASS
                            xml_div = etree.Element('div', {
                                'class': '',
                                'style': 'float: right;',
                                'groups': 'base.group_no_one',
                            })
                            xml_div.text = 'Bypass Fields Attrs'
                            xml_div.append(etree.Element('field', {
                                'name': self._FAH_BYPASS_FIELD,
                                'groups': ','.join(self._FAH_BYPASS_GROUPS_ALL),
                            }))
                            main_node.append(xml_div)

            # - - - - - - -
            # EMBEDDED O2M / M2M FIELDS
            # NOTE: For now, only "tree" and "form".
            # @todo: ? manage other embedded types ? ('graph', 'kanban', 'calendar')
            #        not_supported_embed = doc.xpath("//*[self::graph or self::kanban or self::calendar]")
            
            # Embedded Trees & Forms
            # NOTE: Field injection makes no difference between "tree" or "form",
            #       it always injects at the end of the root.
            #       For now, on embdedded/inline forms it does not look for the possible sheet,
            #       and does not inject helper fields in debug mode.
            for embed_node in doc.xpath("//tree[(ancestor::field)] | //form[(ancestor::field)]"):
                model, rel_field_name, comodel, level = self._get_embedding_model_and_field(view_id, embed_node)
                
                # If the comodel implements the helper's abstract model
                if isinstance(comodel, FieldAttrsHelper):
                    if comodel._FAH_XML_INJECT:
                        for chf_name in comodel._FAH_ATTRS_FIELDS:
                            embed_node.append(etree.Element('field', {
                                'name': chf_name, 
                                'invisible': '0' if comodel._FAH_DEBUG_MODE else '1',
                                'readonly': '0' if comodel._FAH_DEBUG_MODE else '1',
                            }))
                        if embed_node.tag == 'form':
                            xml_div = etree.Element('div', {
                                'class': '',
                                'style': 'float: right;',
                                'groups': 'base.group_no_one',
                            })
                            xml_div.text = 'Bypass Fields Attrs'
                            xml_div.append(etree.Element('field', {
                                'name': comodel._FAH_BYPASS_FIELD,
                                'groups': ','.join(comodel._FAH_BYPASS_GROUPS_ALL),
                            }))
                            embed_node.append(xml_div)

        elif view_type == 'tree':
            if isinstance(self, FieldAttrsHelper):        
                if self._FAH_XML_INJECT:
                    for tree_node in doc.xpath("//tree"):
                        for hf_name in self._FAH_ATTRS_FIELDS:
                            tree_node.append(etree.Element('field', {
                                'name': hf_name, 
                                'invisible': '0' if self._FAH_DEBUG_MODE else '1',
                                'readonly': '0' if self._FAH_DEBUG_MODE else '1',
                            }))
        # Search and Kanban do not seem to require any special attention.
        elif view_type in ('search', 'kanban', 'calendar'):
            pass
        else:
            # pass
            if isinstance(self, FieldAttrsHelper):        
                raise UserError(self._dev_msg(
                    'View type not yet supported: %s' % view_type))

        #---------------------------------------------------------
        # ATTRS FIELDS / NODES
        #---------------------------------------------------------

        # @todo: ?? look at transfer_node_to_modifiers() @ orm.py (core)
        #        modifiers.update(safe_eval(node.get('attrs')))
        #        to obtain pre-existing attrs

        if isinstance(self, FieldAttrsHelper):
            target_fields = self._FAH_FIELD_REGISTRY['model_target_fields']
            target_nodes = self._FAH_FIELD_REGISTRY['model_target_nodes'] # dict node:tag
        
        if view_type == 'form':
            # - - - - - - -
            # MODEL FIELDS
            if isinstance(self, FieldAttrsHelper):
                # Set attrs for all fields not inside embedded/inline views
                if self._FAH_XML_INJECT and self._FAH_XML_INJECT_ATTRS:
                    for tf_name, tags in target_fields.items():            
                        for field_node in doc.xpath("//field[@name='%s' and not (ancestor::field)]" % tf_name):
                            tags_dict = {'model': tags}
                            self._fah_set_field_attrs(self, field_node, 'name', tf_name, current_view_id, tags=tags_dict)
                        
                    for tn_def, tags in target_nodes.items():
                        tag_id, attr_id, attr_val_id = tn_def
                        for elem_node in doc.xpath("//%s[@%s='%s' and not (ancestor::field)]" % (tag_id, attr_id, attr_val_id)):
                        # for elem_node in doc.xpath("//%s[@%s='%s' and not (parent::tree or parent::graph or parent::kanban or parent::calendar)]" % (tag_id, attr_id, attr_val_id)):
                            tags_dict = {'model': tags}
                            self._fah_set_field_attrs(self, elem_node, attr_id, False, current_view_id, tags=tags_dict)

            # - - - - - - -
            # EMBEDDED O2M / M2M FIELDS
            # NOTE: For now only "tree" and "form".
            # @todo: ? manage other embedded types ? ('graph', 'kanban', 'calendar')
            #        not_supported_embed = doc.xpath("//*[self::graph or self::kanban or self::calendar]")
            
            # Embedded Forms
            for form_node in doc.xpath("//form[(ancestor::field)]"):
                # Search for parent
                model, rel_field_name, comodel, level = self._get_embedding_model_and_field(view_id, form_node)

                if isinstance(comodel, FieldAttrsHelper):
                    # Set attrs for all fields not inside embedded/inline views
                    if comodel._FAH_XML_INJECT and comodel._FAH_XML_INJECT_ATTRS:
                        # ______
                        # FIELDS
                        comodel_target_fields = comodel._FAH_FIELD_REGISTRY['model_target_fields']
                        for ctf_name, tags in comodel_target_fields.items():            
                            tags_dict = {'comodel': tags}
                            for field_node in form_node.xpath(".//field[@name='%s']" % ctf_name):
                                if self._get_embedding_model_and_field(view_id, field_node)[3] == level:
                                    self._fah_set_field_attrs(comodel, field_node, 'name', ctf_name, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='comodel_only', tags=tags_dict)
                        # ___________
                        # OTHER NODES
                        comodel_target_nodes = comodel._FAH_FIELD_REGISTRY['model_target_nodes']
                        for ctn_def, tags in comodel_target_nodes.items():
                            tags_dict = {'comodel': tags}
                            tag_id, attr_id, attr_val_id = ctn_def
                            for elem_node in form_node.xpath(".//%s[@%s='%s']" % (tag_id, attr_id, attr_val_id)):
                                if self._get_embedding_model_and_field(view_id, elem_node)[3] == level:
                                    self._fah_set_field_attrs(comodel, field_node, attr_id, False, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='comodel_only', tags=tags_dict)

            # Embedded Trees
            for tree_node in doc.xpath("//tree[(ancestor::field)]"):
                # Search for parent
                model, rel_field_name, comodel, level = self._get_embedding_model_and_field(view_id, tree_node)

                # ______
                # FIELDS
                # Gets the dict with the embedded_target_fields of the current model
                # (those that are driven by this model).
                # NOTE: Unlike model fields, embedded fields are inside a dict whose keys
                #       are the names of the relational fields.
                embedded_target_fields = dict()
                if isinstance(model, FieldAttrsHelper):
                    if model._FAH_XML_INJECT and model._FAH_XML_INJECT_ATTRS:
                        embedded_target_fields = model._FAH_FIELD_REGISTRY['embedded_target_fields']
                rel_embedded_target_fields = embedded_target_fields.get(rel_field_name, dict())
                
                # Gets the dict with the model_target_fields of the comodel
                # (those that are driven by the comodel).
                comodel_target_fields = dict()
                if isinstance(comodel, FieldAttrsHelper):
                    if comodel._FAH_XML_INJECT and comodel._FAH_XML_INJECT_ATTRS:
                        comodel_target_fields = comodel._FAH_FIELD_REGISTRY['model_target_fields']
                
                # Turns the dict keys into a set
                comodel_target_fields_keys = set(comodel_target_fields.keys())
                rel_embedded_target_fields_keys = set(rel_embedded_target_fields.keys())

                # Makes the calculations with the sets
                common_target_fields_keys = comodel_target_fields_keys & rel_embedded_target_fields_keys
                comodel_only_target_fields_keys = comodel_target_fields_keys - rel_embedded_target_fields_keys
                rel_only_target_fields_keys = rel_embedded_target_fields_keys - comodel_target_fields_keys

                # Writes the necessary attributes
                for ctf_name in common_target_fields_keys:
                    rel_embedded_field_tags = rel_embedded_target_fields.get(ctf_name, False)
                    comodel_field_tags = comodel_target_fields.get(ctf_name, False)
                    tags_dict = {'model': rel_embedded_field_tags, 'comodel':comodel_field_tags}
                    for field_node in tree_node.xpath(".//field[@name='%s']" % ctf_name):
                        if self._get_embedding_model_and_field(view_id, field_node)[3] == level:
                            self._fah_set_field_attrs(comodel, field_node, 'name', ctf_name, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='common', tags=tags_dict)
                for ctf_name in comodel_only_target_fields_keys:
                    rel_embedded_field_tags = rel_embedded_target_fields.get(ctf_name, False)
                    comodel_field_tags = comodel_target_fields.get(ctf_name, False)
                    tags_dict = {'model': rel_embedded_field_tags, 'comodel':comodel_field_tags}
                    for field_node in tree_node.xpath(".//field[@name='%s']" % ctf_name):
                        if self._get_embedding_model_and_field(view_id, field_node)[3] == level:
                            self._fah_set_field_attrs(comodel, field_node, 'name', ctf_name, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='comodel_only', tags=tags_dict)
                for ctf_name in rel_only_target_fields_keys:
                    rel_embedded_field_tags = rel_embedded_target_fields.get(ctf_name, False)
                    comodel_field_tags = comodel_target_fields.get(ctf_name, False)
                    tags_dict = {'model': rel_embedded_field_tags, 'comodel':comodel_field_tags}
                    for field_node in tree_node.xpath(".//field[@name='%s']" % ctf_name):
                        if self._get_embedding_model_and_field(view_id, field_node)[3] == level:
                            self._fah_set_field_attrs(comodel, field_node, 'name', ctf_name, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='rel_only', tags=tags_dict)

                # ___________
                # OTHER NODES
                # We get the dict with the embedded_target_nodes of the current model
                # (those that are driven by this model)
                # NOTE: Unlike the model nodes, the embedded nodes are inside a dict whose
                #       keys are the names of the relational fields and this contains another
                #       dict whose keys are the node sets. Inside the sets there are tags.
                embedded_target_nodes = dict()
                if isinstance(model, FieldAttrsHelper):
                    if model._FAH_XML_INJECT and model._FAH_XML_INJECT_ATTRS:
                        embedded_target_nodes = model._FAH_FIELD_REGISTRY['embedded_target_nodes'] # dict of dict rel_field:node:tag
                rel_embedded_target_nodes = embedded_target_nodes.get(rel_field_name, dict()) # dict node:tag
                
                # Gets the dict with the model_target_fields of the comodel
                # (those that are driven by the comodel)
                comodel_target_nodes = dict()
                if isinstance(comodel, FieldAttrsHelper):
                    if comodel._FAH_XML_INJECT and comodel._FAH_XML_INJECT_ATTRS:
                        comodel_target_nodes = comodel._FAH_FIELD_REGISTRY['model_target_nodes'] # dict node:tag
                
                # Turns the dict keys into a set
                comodel_target_nodes_keys = set(comodel_target_nodes.keys())
                rel_embedded_target_nodes_keys = set(rel_embedded_target_nodes.keys())
                
                # Make the calculations with the sets
                common_target_nodes_keys = comodel_target_nodes_keys & rel_embedded_target_nodes_keys
                comodel_only_target_nodes_keys = comodel_target_nodes_keys - rel_embedded_target_nodes_keys
                rel_only_target_nodes_keys = rel_embedded_target_nodes_keys - comodel_target_nodes_keys

                # Writes the necessary attributes
                for ctn_def in common_target_nodes_keys:
                    tag_id, attr_id, attr_val_id = ctn_def
                    rel_embedded_node_tags = rel_embedded_target_nodes.get(ctn_def, False)
                    comodel_node_tags = comodel_target_nodes.get(ctn_def, False)
                    tags_dict = {'model': rel_embedded_node_tags, 'comodel':comodel_node_tags}
                    for elem_node in tree_node.xpath(".//%s[@%s='%s']" % (tag_id, attr_id, attr_val_id)):
                        if self._get_embedding_model_and_field(view_id, elem_node)[3] == level:
                            self._fah_set_field_attrs(comodel, elem_node, attr_id, False, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='common', tags=tags_dict)
                for ctn_def in comodel_only_target_nodes_keys:
                    tag_id, attr_id, attr_val_id = ctn_def
                    rel_embedded_node_tags = rel_embedded_target_nodes.get(ctn_def, False)
                    comodel_node_tags = comodel_target_nodes.get(ctn_def, False)
                    tags_dict = {'model': rel_embedded_node_tags, 'comodel':comodel_node_tags}
                    for elem_node in tree_node.xpath(".//%s[@%s='%s']" % (tag_id, attr_id, attr_val_id)):
                        if self._get_embedding_model_and_field(view_id, elem_node)[3] == level:
                            self._fah_set_field_attrs(comodel, elem_node, attr_id, False, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='comodel_only', tags=tags_dict)
                for ctn_def in rel_only_target_nodes_keys:
                    tag_id, attr_id, attr_val_id = ctn_def
                    rel_embedded_node_tags = rel_embedded_target_nodes.get(ctn_def, False)
                    comodel_node_tags = comodel_target_nodes.get(ctn_def, False)
                    tags_dict = {'model': rel_embedded_node_tags, 'comodel':comodel_node_tags}
                    for elem_node in tree_node.xpath(".//%s[@%s='%s']" % (tag_id, attr_id, attr_val_id)):
                        if self._get_embedding_model_and_field(view_id, elem_node)[3] == level:
                            self._fah_set_field_attrs(comodel, elem_node, attr_id, False, current_view_id, parent_model=model, rel_field_name=rel_field_name, attrs_mode='rel_only', tags=tags_dict)
        
        elif view_type == 'tree':
            if isinstance(self, FieldAttrsHelper):
                if self._FAH_XML_INJECT and self._FAH_XML_INJECT_ATTRS:
                    for tf_name, tags in target_fields.items():            
                        for field_node in doc.xpath("//field[@name='%s']" % tf_name):
                            tags_dict = {'model': tags}
                            self. _fah_set_field_attrs(self, field_node, 'name', tf_name, current_view_id, tags=tags_dict)

                    for tn_def, tags in target_nodes.items():
                        tag_id, attr_id, attr_val_id = tn_def
                        for elem_node in doc.xpath("//%s[@%s='%s']" % (tag_id, attr_id, attr_val_id)):
                            tags_dict = {'model': tags}
                            self._fah_set_field_attrs(self, elem_node, attr_id, False, current_view_id, tags=tags_dict)

        # Search and Kanban do not seem to require any special attention.
        elif view_type in ('search', 'kanban', 'calendar'):
            pass
        else:
            if isinstance(self, FieldAttrsHelper):
                raise UserError(self._dev_msg(
                    'View type not yet supported: %s' % view_type))
            # pass

        res['arch'] = etree.tostring(doc, encoding='unicode')
    
        return res

    # Method to get all necessary information from an embedded node
    def _get_embedding_model_and_field(self, view_id, embedded_arch_node, ancestor_fields=False):
        """ Set a boolean value to an attr on specific target names of a record.
        :param int view_id:                     The ID of the view.
        :param ElementTree embedded_arch_node:  The embedded node as an etree.
        :param list ancestor_fields:            Optional parameter only used internally for recursion.
                                                Do not set at the first call.
        :return:    tuple containing the parent model, parent field name, comodel, nesting level.
        :rtype:     tuple(BaseModel, str, BaseModel, int)
        """  
        parent_node = embedded_arch_node.getparent()
        # If it has reached the root
        if parent_node is None:
            models_chain = [self]
            if ancestor_fields:
                counter = 0
                for rel_field in reversed(ancestor_fields):
                    current_rel_field = getattr(models_chain[counter], rel_field, None)
                    if current_rel_field is not None:
                        models_chain.append(models_chain[counter][rel_field])
                    else:
                        message = f'''Field [ {rel_field} ] does not exist on model [ {models_chain[counter]._name} ].'''
                        self.env['ir.ui.view'].handle_view_error(message) #, view_id)
                    counter += 1
                return (models_chain[-2], ancestor_fields[0], models_chain[-1], len(ancestor_fields))
            else:
                raise UserError(self._dev_msg(
                    'The node passed to the _get_embedding_model_and_field() method is not embedded.'))
        # If it found a parent "field
        elif parent_node.tag == 'field':
            if not ancestor_fields:
                ancestor_fields = list()
            ancestor_fields.append(parent_node.get('name'))
        
        # Whether or not it has found a parent "field".
        return self._get_embedding_model_and_field(view_id, parent_node, ancestor_fields)

    # Method for injecting attrs
    def _fah_set_field_attrs(self, model, node, attr_id, tigger_str, view_id, parent_model=False, rel_field_name=False, attrs_mode=False, tags=False):
        # Checking to avoid overwriting of attrs
        attrs_str = node.get('attrs')
        if attrs_str and model._FAH_XML_INJECT_SAFE:
            err_fn = '_fah_attr_model_target_fields' if node.tag == 'field' else '_fah_get_model_target_nodes'
            raise UserError(model._dev_msg(
                f'''In view [ {str(view_id)} ], the target element [ <{node.tag} {attr_id}="{node.get(attr_id)}"> ] (defined in the property "{err_fn}" of the model) already has the attribute "attrs" set.
                    If possible, remove those "attrs" from the view, directly in the XML.
                    Alternatively, you can remove the field from the target fields declaration.
                    As a last solution, you can deactivate this warning by setting the attribute "_FAH_XML_INJECT_SAFE" on the model to "False".
                    ATTENTION: If you bypass this warning, the domains in the existing attrs will be overwritten (no merge).
                    NOTE: This only applies to target fields.'''
            ))
        else:
            attrs_list = []
            dict_attrs_string = '{ '
            
            # If it is not an embedded field/node
            if parent_model == False:
                delimiter = model._FAH_ATTRS_FIELDS_DELIMITER
                
                # If it's a field
                if node.tag == 'field':
                    for attr, helper_field_name in model._FAH_ATTRS_TUPLES:
                        if attr != 'column_invisible':
                            field_operand = f"('{helper_field_name}', 'like', '{delimiter}{tigger_str}{delimiter}')"
                            attr_operands_list = [field_operand]
                            for tag in tags['model']:
                                attr_operands_list.append(f"('{helper_field_name}', 'like', '{tag}')")

                            full_domain_list = self._fah_compose_domain_or(attr_operands_list)
                            key_attr_string = f"'{attr}': [{','.join(full_domain_list)}]"
                            attrs_list.append(key_attr_string)


                     
                    # NOTE: All targets have force_save="1" because we'll do the checks during write()
                    #       and if you need to force writing on some field, you can put those fields
                    #       in _fah_attr_force_save_fields or use the bypass or the special message
                    #       _FAH_FORCE_COMMAND.
                    # WARNING: If the controls during write and create are not active, setting
                    #          force_save="1" is dangerous!
                    # @todo: We have to set force_save="1" only if the checks are enabled...
                    #        but there is the problem that the check on write and create
                    #        have currently 2 separate options!
                    #        FIX THIS ISSUE!
                    node.set('force_save', '1')
                    # if {'readonly', 'invisible'} & set(parent_model._FAH_ATTRS):
                    #     node.set('force_save', '1')

                # If it is an html element
                else:
                    # It only writes inivisible attr
                    for attr, helper_field_name in model._FAH_ATTRS_TUPLES:
                        if attr == 'invisible':
                            attr_operands_list = []
                            for tag in tags['model']:
                                attr_operands_list.append(f"('{helper_field_name}', 'like', '{tag}')")

                            full_domain_list = self._fah_compose_domain_or(attr_operands_list)
                            key_attr_string = f"'{attr}': [{','.join(full_domain_list)}]"
                            attrs_list.append(key_attr_string)

            # If it is an embedded field/node
            else:
                # If it is a field
                if node.tag == 'field':
                    attrs_dict = dict()
                    if attrs_mode in ['common', 'rel_only']:
                        delimiter = parent_model._FAH_ATTRS_FIELDS_DELIMITER
                        # Compile the domain to the helper field of the parent form
                        for attr, helper_field_name in parent_model._FAH_ATTRS_TUPLES:
                            field_operand = f"('parent.{helper_field_name}', 'like', '{delimiter}{rel_field_name}.{tigger_str}{delimiter}')"
                            if not attrs_dict.get(attr, False):
                                attrs_dict[attr] = list()
                            attrs_dict[attr].append(field_operand)
                            for tag in tags['model']:
                                 attrs_dict[attr].append(f"('parent.{helper_field_name}', 'like', '{tag}')")

                    if attrs_mode in ['common', 'comodel_only']:
                        delimiter = model._FAH_ATTRS_FIELDS_DELIMITER
                        # Compile the domain to the helper field of its embedded tree
                        for attr, helper_field_name in model._FAH_ATTRS_TUPLES:
                            if attr != 'column_invisible':
                                field_operand = f"('{helper_field_name}', 'like', '{delimiter}{tigger_str}{delimiter}')"
                                if not attrs_dict.get(attr, False):
                                    attrs_dict[attr] = list()
                                attrs_dict[attr].append(field_operand)
                                for tag in tags['comodel']:
                                    attrs_dict[attr].append(f"('{helper_field_name}', 'like', '{tag}')")


                    # Compiles the string for the attribute
                    for attr, attr_operands_list in attrs_dict.items():
                        full_domain_list = self._fah_compose_domain_or(attr_operands_list)
                        key_attr_string = f"'{attr}': [{','.join(full_domain_list)}]"
                        attrs_list.append(key_attr_string)
                
                    # NOTE: All embedded targets have force_save="1", as as above, but...
                    # WARNING: As above:
                    #          If the controls during write and create are not active,
                    #          setting force_save="1" is dangerous!
                    #     But there is one more condition...
                    #          Because if the comodel doesn't implement this helper,
                    #          we can't be sure that the checks will be done.
                    # @todo: - check is enabled on write/create?
                    #        - the comodel imoplements this helper?
                    #        FIX THIS ISSUE!
                    node.set('force_save', '1')
                    # if {'readonly', 'invisible'} & set(parent_model._FAH_ATTRS):
                    #     node.set('force_save', '1')

                # If it is an html element
                else:
                    attrs_dict = dict()
                    if attrs_mode in ['common', 'rel_only']:
                        # Compile the domain to the helper field of the parent form
                        for attr, helper_field_name in parent_model._FAH_ATTRS_TUPLES:
                            if attr in ['invisible', 'column_invisible']:
                                attrs_dict[attr] = []
                                for tag in tags['model']:
                                    attrs_dict[attr].append(f"('parent.{helper_field_name}', 'like', '{tag}')")
                    
                    if attrs_mode in ['common', 'comodel_only']:
                        # Compile the domain to the helper field of its embedded tree
                        for attr, helper_field_name in model._FAH_ATTRS_TUPLES:
                            if attr == 'invisible':
                                if not attrs_dict.get(attr, False):
                                    attrs_dict[attr] = []
                                for tag in tags['comodel']:
                                    attrs_dict[attr].append(f"('{helper_field_name}', 'like', '{tag}')")

                    # Compiles the string for the attribute
                    for attr, attr_operands_list in attrs_dict.items():
                        full_domain_list = self._fah_compose_domain_or(attr_operands_list)
                        key_attr_string = f"'{attr}': [{','.join(full_domain_list)}]"
                        attrs_list.append(key_attr_string)

            # Finally, write all the attrs
            dict_attrs_string += ', '.join(attrs_list) + ' }'
            node.set('attrs', dict_attrs_string)

        return node

    # @todo: ! For this method a test must be written with the highest priority !
    #        (I'm not sure if the method of adding an additional '|' at the
    #        beginning, for each pair, is always correct!)
    def _fah_compose_domain_or(self, attr_operands_list):
        """ Compose a full domain in list format.
        :param list attr_operands_list:  List of strings containing a single operand domain tuple;
        :return:  List of strings containing the single operands domain tuples, coupled by "OR"
                  operator (polish notation)
        """

        # If the list contains more than one element
        if len(attr_operands_list) > 1:
            # Create a list containing the sequence of operators and operands (Polish notation)
            full_domain_list = list()
            operands_qty = len(attr_operands_list) # ex. 7
            couples = operands_qty // 2 # ex. 3
            odd_list = operands_qty % 2 # ex. 1
            # If the tags are odd, there should be a condition ALONE, at the beginning
            if odd_list:
                full_domain_list.extend(("'|'", attr_operands_list[-1]))
            current_couple = 1
            while current_couple <= couples:
                operand1 = attr_operands_list[(current_couple*2)-2]
                operand2 = attr_operands_list[(current_couple*2)-1]
                full_domain_list.extend(("'|'", operand1, operand2))
                current_couple +=1
            # It adds (or) operators as much as it needs ;)
            # @todo: check that it is ALWAYS right, for the moment it seems to work...
            for c in range(couples - 1):
                full_domain_list.insert(0, "'|'")
            return full_domain_list
        else:
            return attr_operands_list

        return full_domain_list
