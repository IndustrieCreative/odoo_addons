# -*- coding: utf-8 -*-

from odoo import models, fields
# from odoo.tools.profiler import profile

'''
Attachment finder wizard
'''
class AttachmentRelFinder(models.TransientModel):
    _name = 'base.attachment.relfinder'
    _description = 'Attachment relation finder'
    _rec_name = 'breadcrumb'

    attachment_id = fields.Many2one(
        comodel_name = 'ir.attachment',
        ondelete = 'cascade',
        readonly = True,
        string = 'Attachment',
    )
    relation_ids = fields.One2many(
        comodel_name = 'base.attachment.relfinder.relation',
        inverse_name = 'relfinder_id',
        readonly = True,
        string = 'Found relations'
    )
    breadcrumb = fields.Char(
        default = 'Found relations',
        readonly = True,
    )

    # @profile
    def _find_attachment_relations(self, attachment_id):
        """ Performs the check of attachments in "ir.attachment" according to the parameters passed.

            :param integer attachment_id: Id of the attachment to be searched.
            :return: A list of dictionaries representing the informations about a relation to "ir.attachment"
                     containing 'res_model', 'res_field', 'res_id', 'rel_type' and 'rel_name' keys.
        """
        relations = []
        for model_name in self.env:
            rel_fields = self.env['ir.attachment']._get_model_attachment_relations(model_name)
            if rel_fields == False:
                continue

            m2m_attachment_fields, m2o_attachment_fields = rel_fields

            Model = self.env[model_name]

            for res_m2m_field in m2m_attachment_fields:
                res_records = Model.sudo().with_context(active_test=False).search([
                    (res_m2m_field['name'], 'in', [attachment_id])
                ])
                for res_rec in res_records:
                    relations.append({
                        'res_model': model_name,
                        'res_field': res_m2m_field['name'],
                        'res_id': res_rec.id,
                        'rel_type': 'm2m',
                        'rel_name': res_m2m_field['relation'],
                    })

            for res_m2o_field in m2o_attachment_fields:
                res_records = Model.sudo().with_context(active_test=False).search([
                    (res_m2o_field['name'], '=', attachment_id)
                ])
                for res_rec in res_records:
                    relations.append({
                        'res_model': model_name,
                        'res_field': res_m2o_field['name'],
                        'res_id': res_rec.id,
                        'rel_type': 'm2o',
                        'rel_name': False,
                    })

        return relations


'''
Relations found (the "lines" representing the results of the search)
'''
class AttachmentRelation(models.TransientModel):
    _name = 'base.attachment.relfinder.relation'
    _description = "Attachment relation finder"

    relfinder_id = fields.Many2one(
        comodel_name = 'base.attachment.relfinder',
        ondelete = 'cascade',
        readonly = True,
        string = 'Relation finder',
    )
    res_model = fields.Char(
        readonly = True,
        string = 'Resource Model'
    )
    res_field = fields.Char(
        readonly = True,
        string = 'Resouce Field'
    )
    res_id = fields.Integer(
        readonly = True,
        string = 'Resouce ID'
    )
    rel_type = fields.Selection(
        selection = [('m2m', 'Many2many'),
                     ('m2o', 'Many2one')],
        readonly = True,
        string = 'Relation Type'
    )
    rel_name = fields.Char(
        readonly = True,
        string = 'Many2many relation'
    )

    def action_open_resource(self):
        self.ensure_one()
        return {
            # 'name': 'Found resource',
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }
