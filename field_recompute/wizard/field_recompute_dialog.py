# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from .. tools.fields_recompute import do_fields_recompute, do_record_fields_recompute

class RecomputeField(models.TransientModel):
    _name = 'field.recompute.dialog'
    _description = 'Recompute field tool'
    _rec_name = 'id'
    _order = 'id'

    action = fields.Selection(
        selection = [('field','All record'),('record','One record')],
        required = True,
        default = 'field',
        string = 'Action'
    )
    field_id = fields.Many2one(
        comodel_name = 'ir.model.fields',
        required = True,
        string = 'Field'
    )
    record_ref = fields.Reference(
        selection = '_compute_record_ref_selection',
        string='Model and Record'
    )
    model_id = fields.Many2one(
        comodel_name = 'ir.model',
        string = 'Model'
    )

    # FIELD domain
    @api.onchange('record_ref', 'model_id')
    def _onchange_model(self):
            if self.action == 'field':
                model = self.model_id.model
            elif self.action == 'record':
                if self.record_ref:
                    model = self.record_ref._name #.split(',')[0]
                else:
                    return {'domain': {'field_id': [('id', '=', False)]}}
            else:
                return {
                    'warning': 'Wrong value from "Action" field.',
                    'domain': {'model_id': [('id', '=', False)]}
                }
            model_stored_fields = self.env['ir.model.fields'].search([
                ('store', '=', True),
                ('model', '=', model)
            ], order='model')
            model_computed_stored_fields = model_stored_fields.filtered(lambda field: self.env[field.model_id.model]._fields[field.name].compute)
            return {'domain': {'field_id': [('id', 'in', model_computed_stored_fields.ids)]}}

    # MODEL DOMAIN domain
    @api.onchange('action')
    def _onchange_action(self):
        if self.action == 'field':
            stored_fields_models = self._get_stored_fields_models()
            return {'domain': {'model_id': [('id', 'in', stored_fields_models.ids)]}}

    @api.model
    def _compute_record_ref_selection(self):
        stored_fields_models = self._get_stored_fields_models()
        return [(model.model, model.name) for model in stored_fields_models]
    
    @api.model
    def _get_stored_fields_models(self):
        stored_fields = self.env['ir.model.fields'].search([('store', '=', True)])
        try:
            computed_stored_fields = stored_fields.filtered(lambda field:bool(self.env[field.model_id.model]._fields[field.name].compute) if field.model_id.model in self.env else False)
        except:
            stored_fields_models_ok = self.env['ir.model'].browse([])
        else:
            stored_fields_models = computed_stored_fields.mapped('model_id')
            stored_fields_models_ok = stored_fields_models.filtered(lambda mod: not mod.model.startswith('ir.'))
        finally:
            return stored_fields_models_ok

    def action_execute(self):
        self.ensure_one()
        field = self.field_id.name
        if self.action == 'field':
            model = self.model_id.model
            do_fields_recompute(self.env, model, [field])
        elif self.action == 'record':
            model = self.record_ref._name
            record = self.record_ref
            do_record_fields_recompute(self.env, record, [field])
        else:
            raise UserError('Wrong value from "Action" field.')
