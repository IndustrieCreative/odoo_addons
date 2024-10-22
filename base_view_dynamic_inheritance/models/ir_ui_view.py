from odoo import api, models, fields
from odoo.exceptions import ValidationError

class View(models.Model):
    _inherit = 'ir.ui.view'

    inheritance_group_ids = fields.Many2many(
        comodel_name = 'res.groups',
        relation = 'ir_ui_view_res_group_bvdi_rel',
        column1 = 'view_id',
        column2 = 'group_id',
        string = 'Inheritance Groups',
        help = 'Only on intherited views, if this field is empty, the view '
               'applies to all users. Otherwise, the view applies to the users '
               'of these groups only.'
    )

    # If inheritance_group_ids is not empty, the fields `inherit_id` must be
    # not empty as well, and the `mode` field must be set to 'extension'.
    @api.constrains('inheritance_group_ids', 'inherit_id', 'mode')
    def _check_inheritance_group_ids(self):
        for r in self:
            if r.inheritance_group_ids and (not r.inherit_id or r.mode != 'extension'):
                raise ValidationError(
                    "If the field 'inheritance_group_ids' is populated, inherit_id "
                    "must be populated as well, and mode must be set to 'extension'."
                )

    # Remove views that are not accessible to the current user according to
    # the inheritance_group_ids field. If the field is empty, the view is
    # accessible to all users. Otherwise, the view is accessible to the users
    # of the groups listed in the field.
    def _get_inheriting_views(self):

        res = super()._get_inheriting_views()

        # Get the groups of the current user
        user_groups = self.env.user.groups_id

        # Filter out views where the inheritance_group_ids is not in the user's groups
        filtered_res = res.filtered(
            lambda view:
                not view.inheritance_group_ids or
                (user_groups & view.inheritance_group_ids)
        )

        return filtered_res
