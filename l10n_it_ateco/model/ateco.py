# Copyright (C) 2014 Abstract (<http://abstract.it>).
# Copyright (C) 2016 Ciro Urselli (<http://www.apuliasoftware.it>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AtecoCategory(models.Model):
    _name = "ateco.category"
    _description = "ATECO Code"

    name = fields.Char(required=True)
    code = fields.Char(string="ATECO Code", required=False)
    description = fields.Text()
    parent_id = fields.Many2one("ateco.category", string="Parent Category", index=True)
    child_ids = fields.One2many(
        "ateco.category", "parent_id", string="Child Categories"
    )
    partner_ids = fields.Many2many(
        "res.partner",
        "ateco_category_partner_rel",
        "ateco_id",
        "partner_id",
        string="Partners",
    )

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for record in self:
            if record.code:
                record.display_name = f"{record.code} - {record.name}"
            else:
                record.display_name = record.name
