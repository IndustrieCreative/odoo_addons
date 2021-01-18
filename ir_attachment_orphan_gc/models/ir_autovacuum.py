# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class AutoVacuum(models.AbstractModel):
    _inherit = 'ir.autovacuum'
    
    GC_AV_ACTIVE_PARAM = 'ir.autovacuum.attachment.orphan.active'
    GC_AV_ACTIVE_DEFAULT = False # boolean
    
    GC_AV_UNLINK_PARAM = 'ir.autovacuum.attachment.orphan.unlink'
    GC_AV_UNLINK_DEFAULT = False # boolean

    GC_AV_WEEKDAY_PARAM = 'ir.autovacuum.attachment.orphan.weekday'
    GC_AV_WEEKDAY_DEFAULT = False # datetime.date.weekday() integer from 0 to 6 or False

    @api.model
    def power_on(self, *args, **kwargs):
        
        # Get cron active status System Parameter
        gc_active = self.env['ir.config_parameter'].sudo().get_param(self.GC_AV_ACTIVE_PARAM, 'not-set')
        if gc_active == 'not-set':
            gc_active = self.GC_AV_ACTIVE_DEFAULT
            self.env['ir.config_parameter'].sudo().set_param(self.GC_AV_ACTIVE_PARAM, str(gc_active))
        elif gc_active == 'True':
            gc_active = True
        elif gc_active == 'False':
            gc_active = False
        else:
            gc_active = self.GC_AV_ACTIVE_DEFAULT
            _logger.info('ATTACHMENTS GC - The System Parameter "%s" must be a string "True" or "False", case sensitive. Default value will be used (%s).' % (
                self.GC_AV_ACTIVE_PARAM,
                str(gc_active)
            ))

        # Get weekday limitation System Parameter
        gc_weekday = self.env['ir.config_parameter'].sudo().get_param(self.GC_AV_WEEKDAY_PARAM, 'not-set')
        if gc_weekday == 'not-set':
            gc_weekday = self.GC_AV_WEEKDAY_DEFAULT
            self.env['ir.config_parameter'].sudo().set_param(self.GC_AV_WEEKDAY_PARAM, str(gc_weekday))
        elif gc_weekday.isdigit():
            gc_weekday = int(gc_weekday)
            if (gc_weekday < 0) or (gc_weekday > 6):
                gc_weekday = self.GC_AV_WEEKDAY_DEFAULT
                _logger.info('ATTACHMENTS GC - The System Parameter "%s" must be a "datetime.date.weekday()" number from "0" to "6" or "False", case sensitive. Default value will be used (%s).' % (
                    self.GC_AV_WEEKDAY_PARAM,
                    str(gc_weekday)
                ))
        elif gc_weekday == 'False':
            gc_weekday = False
        else:
            gc_weekday = self.GC_AV_WEEKDAY_DEFAULT
            _logger.info('ATTACHMENTS GC - The System Parameter "%s" must be a "datetime.date.weekday()" number from "0" to "6" or "False", case sensitive. Default value will be used (%s).' % (
                self.GC_AV_WEEKDAY_PARAM,
                str(gc_weekday)
            ))

        # Apply weekday limitation if necessary
        if gc_weekday and gc_weekday != fields.Date.today().weekday():
            gc_active = False
            _logger.info('ATTACHMENTS GC - According to the System Parameter "%s" that is set to  "%s", today this garbage collector will not be executed.' % (
                self.GC_AV_WEEKDAY_PARAM,
                str(gc_weekday)
            ))

        if gc_active:
            # Get cron unlink System Parameter
            gc_do_unlink = self.env['ir.config_parameter'].sudo().get_param(self.GC_AV_UNLINK_PARAM, 'not-set')
            if gc_do_unlink == 'not-set':
                gc_do_unlink = self.GC_AV_UNLINK_DEFAULT
                self.env['ir.config_parameter'].sudo().set_param(self.GC_AV_UNLINK_PARAM, str(gc_do_unlink))
            elif gc_do_unlink == 'True':
                gc_do_unlink = True
            elif gc_do_unlink == 'False':
                gc_do_unlink = False
            else:
                gc_do_unlink = self.GC_AV_UNLINK_DEFAULT
                _logger.info('ATTACHMENTS GC - The System Parameter "%s" must be a string "True" or "False", case sensitive. Default value will be used (%s).' % (
                    self.GC_AV_UNLINK_PARAM,
                    str(gc_do_unlink)
                ))

            # Execute the cron
            self.env['ir.attachment']._garbage_collect_rel_orphan_attachments(do_unlink=gc_do_unlink)
            
        return super(AutoVacuum, self).power_on(*args, **kwargs)
