# -*- coding: utf-8 -*-

from odoo import api, models

class AutoVacuum(models.AbstractModel):
    _inherit = 'ir.autovacuum'

    @api.model
    def power_on(self, *args, **kwargs):
        self.env['ir.attachment'].orphan_attachments_garbage_collector()
        return super(AutoVacuum, self).power_on(*args, **kwargs)
