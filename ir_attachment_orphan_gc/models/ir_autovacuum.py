# -*- coding: utf-8 -*-

import logging
from odoo import models

_logger = logging.getLogger(__name__)

class AutoVacuum(models.AbstractModel):
    _inherit = 'ir.autovacuum'
    
    # Overrided (instead of using @api.autovacuum decorator) in order
    # to execute the _gc_orphan_attachments_autovacuum() method as last,
    # after all transient records are deleted (because some transient models
    # could use Attachments).
    def _run_vacuum_cleaner(self):
        super(AutoVacuum, self)._run_vacuum_cleaner()
        _logger.debug('Calling ir.attachment()._gc_orphan_attachments_autovacuum()')
        try:
            self.env['ir.attachment']._gc_orphan_attachments_autovacuum()
            self.env.cr.commit()
        except Exception:
            _logger.exception('Failed ir.attachment()._gc_orphan_attachments_autovacuum()')
            self.env.cr.rollback()
