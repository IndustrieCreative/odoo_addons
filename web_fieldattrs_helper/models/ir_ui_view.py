# -*- coding: utf-8 -*-
# from lxml import etree
from odoo import fields, models
from . web_fieldattrs_helper import FieldAttrsHelper

# Override for the sole purpose of showing at runtime on the UI
# if and how a view has been changed by this helper.
class View(models.Model):
    _inherit = 'ir.ui.view'

    fah_implemented = fields.Text(
        string = 'FAH active?',
        compute = '_compute_fah_model_info',
    )
    fah_model_status = fields.Text(
        string = 'FAH Status on this model',
        compute = '_compute_fah_model_info',
    )
    fah_overridden_view = fields.Text(
        string = 'FAH Overridden View',
        compute = '_compute_fah_overridden_view',
        store = False
    )

    def _compute_fah_model_info(self):
        for r in self:
            model = self.env['ir.model'].sudo().search([('model', '=', r.model)])
            r.fah_implemented = model.fah_implemented
            r.fah_model_status = model.fah_model_status

    def _compute_fah_overridden_view(self):
        for r in self:
            r.fah_overridden_view = False
            if r.model:
                Model = self.env[r.model]
                if isinstance(Model, FieldAttrsHelper):
                    view = Model._fields_view_get(view_id=r.id, view_type=r.type)
                    r.sudo().fah_overridden_view = view['arch']


    # !! CURRENTLY DEACTIVATED !!
    # This override is not needed if you do NOT need to give the option
    # to to place the attrs manually on the view.
    # 
    # I would say that it is better to remove this possibility, otherwise all views will
    # break when the code is changed (as happens all the time ;)). This way, if you want
    # to temporarily deactivate the helper completely, you can always do so.
    # @todo: If this is OK, remove the _FAH_XML_INJECT_ATTRS option and keep only _FAH_XML_INJECT
    # 
    # Override to postprocess() which allows:
    # - Adding "attrs" to xml elements that are not "fields" only if "_FAH_XML_INJECT" is
    #   set to "True" (this is because "attr" obviously has to point to helper fields that
    #   are dynamically injected).
    # THIS IS BECAUSE: When loading/updating the module, the view is checked without going
    #                  through _fields_view_get(), so odoo would say that it can't find the
    #                  helper fields..
    # 
    # ??: At this point it would make sense to transfer all the code of _fields_view_get()
    #     here.
    # !!: If this is the case, check that the "arch" stored in the DB has not been altered,
    #     as it would no longer be possible to (easily) compare the original and overridden
    #     views.
    #   
    # @todo: Check that, now that it works, it is not possible to execute it directly in
    #        postprocess_and_fields() (so it should execute less times...?).
    # @todo: DUPLICATED HELPER FIELDS ON VIEW!! Move the _fields_view_get() part here
    #        (or to postprocess_and_fields()), so that we can inject directly from here,
    #        since these two methods are evidently executed both when updating the form
    #        and when requesting the view.
    # NOTE: The field_view_get() uses postprocess() to check if the view has been modified
    #       from the debug tool instead on the xml file.
    #
    #
    # @api.model
    # def postprocess(self, model, node, view_id, in_tree_view, model_fields):
    #     Model = self.env[model]
    #     # If the template implements this helper
    #     if isinstance(Model, FieldAttrsHelper):
    #         # If XML injection is active
    #         if Model._FAH_XML_INJECT:
    #             # Only in case of "form"
    #             if node.tag == 'form':
    #                 # Adds helper fields to the "sheet".
    #                 for sheet_node in node.xpath("//sheet"):
    #                     for hf_name in Model._FAH_ATTRS_FIELDS:
    #                         xml_field = etree.Element('field', {
    #                             'name': hf_name, 
    #                             'debug': 'INJECT SHEET @ postprocess()',
    #                             'invisible': '1',
    #                             'readonly': '1',
    #                         })
    #                         sheet_node.append(xml_field)
    #     # Returns the modified node to the original function.
    #     return super(View, self).postprocess(model, node, view_id, in_tree_view, model_fields)
