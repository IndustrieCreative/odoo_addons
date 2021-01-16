# -*- coding: utf-8 -*-

from odoo import api, models

class AutoVacuum(models.AbstractModel):
    _inherit = 'ir.autovacuum'

    @api.model
    def power_on(self, *args, **kwargs):
        self.env['ir.attachment']._garbage_collect_rel_orphan_attachments()
        return super(AutoVacuum, self).power_on(*args, **kwargs)
