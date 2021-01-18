# -*- coding: utf-8 -*-

from odoo import fields, models

class IrModel(models.Model):
    _inherit = 'ir.model'

    attachment_gc_active = fields.Boolean(
        compute = '_compute_attachment_gc_active',
        search = '_search_attachment_gc_active',
        string = 'GC active?',
        store = False,
        help = '''"True" if this model has the "_attachment_garbage_collector" attribute set to "True" in its Python class definition.'''
    )

    def _compute_attachment_gc_active(self):
        for r in self:
            if self.env.get(r.model) is not None:
                r.attachment_gc_active = getattr(self.env[r.model], '_attachment_garbage_collector', False)

    def _search_attachment_gc_active(self, operator, value):
        active_model_ids = []
        for model in self.search([]):
            if self.env.get(model.model) is not None:
                if getattr(self.env[model.model], '_attachment_garbage_collector', False):
                    active_model_ids.append(model.id)
        # Bypass search operator
        if operator == '=':
            return [('id', 'in', active_model_ids)]
        elif operator == '!=':
            return [('id', 'not in', active_model_ids)]

    def action_gc_rel_orphan_attachments_safe(self):
        self.ensure_one()
        self.env['ir.attachment']._garbage_collect_rel_orphan_attachments(
            force_models=[self.model],
            do_unlink=False
        )
    def action_gc_rel_orphan_attachments_unlink(self):
        self.ensure_one()
        self.env['ir.attachment']._garbage_collect_rel_orphan_attachments(
            force_models=[self.model],
            do_unlink=True
        )

    def action_open_attachments(self):
        self.ensure_one()
        # view_tree_id = self.env.ref('asc_monitoraggio.asc_monitoraggio_iscrizione_presenza_view_tree').id
        # view_form_id = self.env.ref('asc_monitoraggio.asc_monitoraggio_iscrizione_presenza_view_form').id

        return {
            'name': 'Attachments',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            # 'view_id': view_tree_id,
            # 'views': [(view_tree_id, 'tree'), (view_form_id, 'form')],
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('res_model', '=', self.model)],
            'context': {
                'default_res_model': self.model,
            } 
        }
