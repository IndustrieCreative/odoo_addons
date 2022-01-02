# -*- coding: utf-8 -*-

import logging
from odoo import fields, models
# from odoo.tools.profiler import profile

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    CG_MODULE_NAME_SAFELIST = []
    CG_MODULE_PREFIX_SAFELIST = ['ir.']

    maybe_orphan = fields.Boolean(
        readonly = True,
        string = 'Maybe orphan?',
        help = '''"True" if this attachment was found to be orphaned during the last check
            by _garbage_collect_rel_orphan_attachments(). If the attachment is found to be
            orphaned during the next check as well, it will be deleted. Otherwise this flag
            will be removed.'''
    )

    def action_find_resource(self):
        self.ensure_one()
        
        Relfinder = self.env['base.attachment.relfinder']
        found_relations = Relfinder._find_attachment_relations(self.id)
        new_relfinder = Relfinder.create({
            'attachment_id': self.id,
            # Create a "line" for each relation
            'relation_ids': [(0, 0, {
                'res_model': rel['res_model'],
                'res_field': rel['res_field'],
                'res_id': rel['res_id'],
                'rel_type': rel['rel_type'],
                'rel_name': rel['rel_name'],
            }) for rel in found_relations]
        })

        return {
            'name': 'Found resources',
            'type': 'ir.actions.act_window',
            'res_model': 'base.attachment.relfinder',
            'res_id': new_relfinder.id,
            'view_mode': 'form',
            'target': 'current',
        }

    # @profile
    def _get_model_attachment_relations(self, model_name):
        """ Performs the check of attachments in "ir.attachment" according to the parameters passed.

            :param string model_name: The name of the model in which to search for Many2many and Many2one fields related to 'ir.attachment'.
            :return: tuple.
                [0]: A dictionary representing the informations about a Many2many field, containing 'name', 'relation', 'column1', 'column2' keys.
                [1]: A dictionary representing the informations about a Many2one field, containing 'name' key
        """

        Model = self.env[model_name]
        # Trova tutti i campi many2many e many2one del modello che puntano a 'ir.attachment'
        m2m_attachment_fields = []
        m2o_attachment_fields = []
        if not Model._abstract and model_name != 'base.attachment.relfinder':
            fields_dict = Model.fields_get([], ['type', 'relation', 'store'])
            for field_name, field_attrs in fields_dict.items():
                model_field = Model._fields.get(field_name)
                # Only stored and not inherited fields (from _inherits)   
                if field_attrs.get('store') and not model_field.inherited:
                    if field_attrs.get('type') == 'many2many' and field_attrs.get('relation') == 'ir.attachment':
                        m2m_attachment_fields.append({
                            'name': field_name,
                            'relation': model_field.relation,
                            'column1': model_field.column1,
                            'column2': model_field.column2
                        })
                    elif field_attrs.get('type') == 'many2one' and field_attrs.get('relation') == 'ir.attachment':
                        m2o_attachment_fields.append({
                            'name': field_name
                        })
                    else:
                        continue
                else:
                    continue
        else:
            return False

        return m2m_attachment_fields, m2o_attachment_fields


    # @profile
    def _garbage_collect_rel_orphan_attachments(self, do_unlink=False, force_models=False):
        """ Performs the check of attachments in "ir.attachment" according to the parameters passed.

            :param bool do_unlink: If True perform unlink(), if False mark only.
            :param list force_models: List of strings containing the names of the models to be checked.
            :return: True
        """
        self = self.sudo()

        _logger.info('ATTACHMENTS GC - STARTED' + ('.' if do_unlink else ' in safe mode.'))
        count = {'model': 0, 'm2m': 0, 'm2o': 0}

        # Prepara la safelist effettiva
        cg_name_safelist = [ model_name
            for model_name in self.env if model_name[0:3] in self.CG_MODULE_PREFIX_SAFELIST
        ]
        cg_name_safelist = list(set(cg_name_safelist + self.CG_MODULE_NAME_SAFELIST))
        _logger.info('ATTACHMENTS GC - The model safelist is: %s' % ', '.join(cg_name_safelist))

        # Tutti i modelli che hanno campi Many2many o Many2one che puntano a "ir.attachemnt"
        rel_models = []
        # Tutti i modellli attivi
        act_models = []
        for model_name in self.env:
            
            rel_fields = self._get_model_attachment_relations(model_name)
            if rel_fields == False:
                continue # If no related fields are found, pass to the next model
            
            m2m_attachment_fields, m2o_attachment_fields = rel_fields

            if force_models:
                is_active_model = True if model_name in force_models else False
            else:                 
                # Legge l'attributo che attiva il gc sul modello
                is_active_model = getattr(self.env[model_name], '_attachment_garbage_collector', False)
                # Valida il tipo dell'attributo
                if type(is_active_model) is not bool:
                    is_active_model = False
                    _logger.warning('ATTACHMENTS GC - The "_attachment_garbage_collector" attribute of the model "%s" is not boolean. The attriburte has been ignored.' % model_name)
            
            # Ignora come attivi i modelli nella safelist
            if is_active_model and (model_name in cg_name_safelist):
                is_active_model = False
                _logger.warning('ATTACHMENTS GC - According to the safelist, the model "%s" cannot be active. The attachments of this model have been ignored.' % model_name)

            # Se punta a "ir.attachment" o è un modello attivo
            if m2m_attachment_fields or m2o_attachment_fields:
                rel_models.append({
                    'model_name': model_name,
                    'm2m_attachment_fields': m2m_attachment_fields,
                    'm2o_attachment_fields': m2o_attachment_fields
                })
                count['model'] += 1
                count['m2m'] += len(m2m_attachment_fields)
                count['m2o'] += len(m2o_attachment_fields)

            if is_active_model:
                act_models.append(model_name)

            if is_active_model and not (m2m_attachment_fields or m2o_attachment_fields):
                _logger.warning('ATTACHMENTS GC - The active model "%s" does not appear to have any relational fields (m2m or m2o) pointing to "ir.attachment".' % model_name)

        _logger.info('ATTACHMENTS GC - %d  Many2many and  %d  Many2one fields related to "ir.attachment" were found on  %d  different models.' % (count['m2m'], count['m2o'], count['model']))
        _logger.info('ATTACHMENTS GC - The service %s on this  %d  models: %s' % (
            ('is forced to be active' if force_models else 'is active'),
            len(act_models),
            ', '.join(act_models))
        )

        # Tutti gli attachment associati ai modelli "attivi" con "res_model" ma senza "res_id"
        all_active_models_attachments = self.sudo().with_context(active_test=False).search([
            '&',
                ('res_model', 'in', act_models),
                '|', # Così non tocca gli attachment dei messaggi nel chatter, che
                     # sono già gestiti dal "mail.thread" mixin. 
                     # Gli attachment dei campi Binary (con "attachment=True") vengono
                     # già nascosti da _search() se il campo "res_field" o "id" non è
                     # presente nel dominio (hard-coded record rule).
                    ('res_id', '=', 0), # Di solito viene scritto 0...
                    ('res_id', '=', False) # ma a volte portebbe essere False.
                    # NB: [('res_id','=',0), ('res_field','!=',False)] sembra non debba
                    #     mai accadere. Controllare di nuovo in futuro.
        ])
        
        _logger.info('ATTACHMENTS GC - In the active models,  %d  attachments were found which need to be checked.' % len(all_active_models_attachments))

        # Tutti gli attachment dei modelli "attivi" usati da record di qualunque altro modello
        used_attachments = self.env['ir.attachment'] # empty recordset
        for model in rel_models:
            Model = self.env[model['model_name']]

            for res_m2m_field in model['m2m_attachment_fields']:
                self.env.cr.execute('SELECT %s FROM %s' % (res_m2m_field['column2'], res_m2m_field['relation']))
                m2m_field_used_attachments_ids = [id[0] for id in self.env.cr.fetchall()]
                m2m_field_used_attachments = self.sudo().browse(m2m_field_used_attachments_ids)

                used_attachments |= m2m_field_used_attachments

            for res_m2o_field in model['m2o_attachment_fields']:
                m2o_field_used_attachments = Model.sudo().with_context(active_test=False).search([
                    (res_m2o_field['name'], '!=', False)
                ]).mapped(res_m2o_field['name'])
                
                used_attachments |= m2o_field_used_attachments


        # Individua gli attachment orfani
        orphan_attachments = all_active_models_attachments - used_attachments
        # Gli attachment che sono stati marcati precedentemente, ma ora non risultano più orfani
        not_orphan_attachments = used_attachments.filtered('maybe_orphan')
        # Gli attachment che erano già marcati
        confirmed_orphan_attachments = orphan_attachments.filtered('maybe_orphan')
        # Gli attachment non ancora marcati, e da marcare
        maybe_orphan_attachments = orphan_attachments - confirmed_orphan_attachments

        count['oa'] = len(orphan_attachments)
        count['coa'] = len(confirmed_orphan_attachments)
        count['poa'] = len(maybe_orphan_attachments)

        # Esegue le operazioni
        if do_unlink:
            confirmed_orphan_attachments.sudo().unlink()
        maybe_orphan_attachments.sudo().write({'maybe_orphan': True})
        not_orphan_attachments.sudo().write({'maybe_orphan': False})

        _logger.info('ATTACHMENTS GC - DONE.')
        _logger.info('ATTACHMENTS GC - Found  %d  possible orphan attachments on the active models.' % count['oa'])
        if do_unlink:
            _logger.info('ATTACHMENTS GC - DELETED  %d  confirmed orphan attachments.' % count['coa'])
        else:
            _logger.info('ATTACHMENTS GC - SKIPPED  %d  confirmed orphan attachments (not deleted).' % count['coa'])
        _logger.info('ATTACHMENTS GC - MARKED  %d  new possible orphan attachments.' % count['poa'])

        return True

        # REMEMBER THAT...
        # Attachments left orphaned during the creation of a message/note/email
        # (while still in a transient) that eventually failed are already deleted by
        # self.emv['mail.thread']._garbage_collect_attachments(). In practice, this
        # deletes attachments with ('res_model', '=', 'mail.compose.message') created
        # or modified at least one day before.


    # @todo: Implementare registro/log degli attachment cancellati (hash, tipo, dimensione, res_name, res_model)
    # @todo: Implementare action multi "set as not orphan"
    # @todo: ?? Aggiungere constraint che dà errore se si marcano record con "res_id" != False ??
