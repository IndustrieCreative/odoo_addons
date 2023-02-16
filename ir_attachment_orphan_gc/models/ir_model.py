# -*- coding: utf-8 -*-

# import time
from odoo import fields, models, api

class IrModel(models.Model):
    _inherit = 'ir.model'

    attachment_gc_active = fields.Boolean(
        compute = '_compute_attachment_gc_active',
        search = '_search_attachment_gc_active_autovacuum',
        string = 'GC active?',
        store = False,
        help = '"True" if this model has the "_attachment_garbage_collector" '
            'attribute set to "True" in its Python class definition.\n'
            'If this is active and the System patameter "ir.autovacuum.attachment.orphan.active" '
            'is set to "True", the attachments of this Model will be processed '
            'during the Cron "Base: Auto-vacuum internal data".'
    )
    attachment_gc_active_not_o2m = fields.Boolean(
        compute = '_compute_attachment_gc_active',
        search = '_search_attachment_gc_active_not_o2m',
        string = 'GC not O2M?',
        store = False,
        help = '"True" if this model has the "_attachment_garbage_collector_not_o2m" '
            'attribute set to "True" in its Python class definition.\n'
            'If this is active the orphanity of the attachments is evaluated only '
            'through m2m or m2o relations. Is "False" by default. If it is "False" '
            'also the o2m relations are evaluated (more safe).'
    )

    def _compute_attachment_gc_active(self):
        for r in self:
            if self.env.get(r.model) is not None:
                r.attachment_gc_active = getattr(self.env[r.model], '_attachment_garbage_collector', False)
                r.attachment_gc_active_not_o2m = getattr(self.env[r.model], '_attachment_garbage_collector_not_o2m', False)

    def _search_attachment_gc_active(self, operator, value, attribute):
        active_model_ids = []
        for model in self.search([]):
            if self.env.get(model.model) is not None:
                if getattr(self.env[model.model], attribute, False):
                    active_model_ids.append(model.id)
        # Bypass search operator
        if operator == '=':
            return [('id', 'in', active_model_ids)]
        elif operator == '!=':
            return [('id', 'not in', active_model_ids)]

    def _search_attachment_gc_active_not_o2m(self, operator, value):
        return self._search_attachment_gc_active(operator, value, '_attachment_garbage_collector_not_o2m')
    
    def _search_attachment_gc_active_autovacuum(self, operator, value):
        return self._search_attachment_gc_active(operator, value, '_attachment_garbage_collector')

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
        return {
            'name': 'Attachments',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('res_model', '=', self.model)],
            'context': {
                'default_res_model': self.model,
            } 
        }

    # RPC API FOR CHATTER
    @api.model
    def get_attachment_gc_mode(self, model_name):
        # @test: Delay response for some seconds;
        #        to check if the Chatter is re-rendering after
        #        the form is loaded.
        # time.sleep(5)
        model = self.search([("model", "=", model_name)])
        return 'not-o2m' if model.attachment_gc_active_not_o2m else 'o2m'
