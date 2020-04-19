# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.exceptions import UserError

class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def get_inheriting_views_arch(self, view_id, model):

        res = super(View, self).get_inheriting_views_arch(view_id, model)
        viewS_to_add = self.env.context.get('bvdi_force_add_inheriting_views', False)

        if viewS_to_add:
            for view_to_add in viewS_to_add:
                if view_to_add['view_id'] == view_id:
                    inherit_view = self.search([('id', '=', view_to_add['inherit_view_id'])])

                    if view_to_add['inherit_position'] == 'append':
                        res.append((inherit_view.arch, inherit_view.id))
                        # res.insert(-1, (inherit_view.arch, inherit_view.id))
                    elif view_to_add['inherit_position'] == 'prepend':
                        # res.prepend((inherit_view.arch, inherit_view.id))
                        res.insert(0, (inherit_view.arch, inherit_view.id))
                    else:
                        raise UserError("The key 'view_position' in the dict 'bvdi_force_add_inheriting_views' has an unattended value! ")
        else:
            pass

        return res
