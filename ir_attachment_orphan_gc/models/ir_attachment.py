# -*- coding: utf-8 -*-

import logging
# import datetime
from io import StringIO
# from dateutil.parser import isoparse
from odoo import fields, models #, api
# from odoo.tools.profiler import profile

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    CG_MODEL_NAME_SAFELIST = ['mail.channel', 'website', 'calendar.event']
    CG_MODEL_PREFIX_SAFELIST = ['ir.']
    CG_MODEL_FIELD_IGNORELIST = ['message_main_attachment_id']
    CG_IGNORE_LAST_EDIT_DAYS = 2

    GC_AV_ACTIVE_PARAM = 'ir.autovacuum.attachment.orphan.active'
    GC_AV_ACTIVE_DEFAULT = False # boolean
    
    GC_AV_UNLINK_PARAM = 'ir.autovacuum.attachment.orphan.unlink'
    GC_AV_UNLINK_DEFAULT = False # boolean

    GC_AV_WEEKDAY_PARAM = 'ir.autovacuum.attachment.orphan.weekday'
    GC_AV_WEEKDAY_DEFAULT = False # datetime.date.weekday() integer from 0 to 6 or False

    maybe_orphan = fields.Boolean(
        readonly = True,
        string = 'Maybe orphan?',
        help = '''"True" if this attachment was found to be orphaned during the last check
            by _garbage_collect_rel_orphan_attachments(). If the attachment is found to be
            orphaned during the next check as well, it will be deleted. Otherwise this flag
            will be removed.'''
    )

    def action_uncheck_maybe_orphan(self):
        self.write({'maybe_orphan': False})

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
        # Store the logger output to a string stream handler
        logger = logging.getLogger(__name__)
        log_stream = StringIO()
        stream_handler = logging.StreamHandler(log_stream)
        logger.addHandler(stream_handler)

        self = self.sudo()

        logger.info('ATTACHMENTS GC - STARTED' + ('.' if do_unlink else ' in safe mode.'))
        count = {'model': 0, 'm2m': 0, 'm2o': 0}

        # Prepara la safelist effettiva
        cg_name_safelist = [ model_name
            for model_name in self.env if model_name[0:3] in self.CG_MODEL_PREFIX_SAFELIST
        ]
        cg_name_safelist = list(set(cg_name_safelist + self.CG_MODEL_NAME_SAFELIST))
        logger.info('ATTACHMENTS GC - The model safelist is: %s' % ', '.join(cg_name_safelist))

        # Tutti i modelli che hanno campi Many2many o Many2one che puntano a "ir.attachemnt"
        rel_models = [] # list(dict)
        # Tutti i modelli attivi che hanno _attachment_garbage_collector_o2m == True
        o2m_models = [] # list(Model)
        # Tutti i modellli attivi
        act_models = [] # list(str)
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
                    logger.warning('ATTACHMENTS GC - The "_attachment_garbage_collector" attribute of the model "%s" is not boolean. The attriburte has been ignored.' % model_name)
            
            # Ignora come attivi i modelli nella safelist
            if is_active_model and (model_name in cg_name_safelist):
                is_active_model = False
                logger.warning('ATTACHMENTS GC - According to the safelist, the model "%s" cannot be active. The attachments of this model have been ignored.' % model_name)

            # Se punta a "ir.attachment"
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

                # Legge l'attributo che disattiva l'opzione o2m gc sul modello
                is_not_o2m_model = getattr(self.env[model_name], '_attachment_garbage_collector_not_o2m', False)
                # Valida il tipo dell'attributo
                if type(is_not_o2m_model) is not bool:
                    is_not_o2m_model = False
                    logger.warning('ATTACHMENTS GC - The "_attachment_garbage_collector_not_o2m" attribute of the model "%s" is not boolean. The attriburte has been ignored.' % model_name)
                if not is_not_o2m_model:
                    # Popola la lista dei modelli con l'opzione "o2m" attiva
                    o2m_models.append(self.env[model_name])

                if is_not_o2m_model and not m2m_attachment_fields and not m2o_attachment_fields:
                    logger.warning('ATTACHMENTS GC - The active model "%s" does not appear to have any relational fields (m2m or m2o) pointing to "ir.attachment" and the O2M mode is disabled.' % model_name)

        logger.info('ATTACHMENTS GC - %d  Many2many and  %d  Many2one fields related to "ir.attachment" were found on  %d  different models.' % (count['m2m'], count['m2o'], count['model']))
        logger.info('ATTACHMENTS GC - The service %s on  %d  models: %s' % (
            ('is forced to be active' if force_models else 'is active'),
            len(act_models),
            ', '.join(act_models))
        )
        logger.info('ATTACHMENTS GC - The O2M mode is enabled on  %d  active models: %s' % (
            len(o2m_models),
            ', '.join([model._name for model in o2m_models]))
        )

        # Check if all Attachments that meet the following conditions are orphaned:
        # - linked to any res_model in "act_models" list
        # - unused since at least one day (create_date and write_date) so as to
        #   exclude files uploaded via the Chatter, via "many2many_binary" or
        #   reports created on-the-fly.
        # NOTE: Binary fields are auto excluded by _search() override on ir.attachment
        #       if "id" or "res_field" aren't in the search domain.
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=self.CG_IGNORE_LAST_EDIT_DAYS)
        all_active_models_attachments = self.sudo().with_context(active_test=False).search([
            ('res_model', 'in', act_models),
            # ('create_date', '<', limit_date),
            # ('write_date', '<', limit_date)
        ])
        
        logger.info('ATTACHMENTS GC - In the active models,  %d  attachments were found which need to be checked.' % len(all_active_models_attachments))

        # Tutti gli attachment dei modelli "attivi" usati da record di qualunque
        # altro modello tramite campi m2m o m2o
        rel_used_attachments = self.env['ir.attachment'] # empty recordset
        
        # Tutti gli attachment dei modelli "attivi" che puntano a record
        # ancora esistenti
        o2m_used_attachments = self.env['ir.attachment'] # empty recordset
        
        for rel_model in rel_models:
            Model = self.env[rel_model['model_name']]
            
            # Campi M2M
            for res_m2m_field in rel_model['m2m_attachment_fields']:
                self.env.cr.execute('SELECT %s FROM %s' % (res_m2m_field['column2'], res_m2m_field['relation']))
                m2m_field_used_attachments_ids = [id[0] for id in self.env.cr.fetchall()]
                m2m_field_used_attachments = self.sudo().browse(m2m_field_used_attachments_ids)

                rel_used_attachments |= m2m_field_used_attachments

            # Campi M2O
            for res_m2o_field in rel_model['m2o_attachment_fields']:
                if res_m2o_field['name'] not in self.CG_MODEL_FIELD_IGNORELIST:
                    m2o_field_used_attachments = Model.sudo().with_context(active_test=False).search([
                        (res_m2o_field['name'], '!=', False)
                    ]).mapped(res_m2o_field['name'])
                
                    rel_used_attachments |= m2o_field_used_attachments

        # Ottiene gli attachment orfani da relazioni
        rel_orphan_attachments = all_active_models_attachments - rel_used_attachments

        # Individua gli attachment che puntano a record ancora esistenti
        # tra quelli orfani da relazioni
        for o2m_model in o2m_models:
            self.env.cr.execute('SELECT id FROM %s' % o2m_model._table)
            o2m_model_record_ids = [id[0] for id in self.env.cr.fetchall()]
            o2m_used_attachments |= rel_orphan_attachments.filtered(lambda a:
                a.res_model == o2m_model._name and \
                a.res_id in o2m_model_record_ids
            )

        # Aggiunge gli attachment che puntano a record ancora esistenti
        # agli attachment usati da relazioni
        used_attachments = rel_used_attachments | o2m_used_attachments

        # Sottrae gli attachment che puntano a record ancora esistenti
        # agli attachment orfani da relazioni
        all_orphan_attachments = rel_orphan_attachments - o2m_used_attachments

        # Gli attachment che sono stati marcati precedentemente, ma ora non risultano più orfani
        not_orphan_attachments = used_attachments.filtered('maybe_orphan')
        # Gli attachment che erano già marcati
        confirmed_orphan_attachments = all_orphan_attachments.filtered('maybe_orphan')
        # Gli attachment non ancora marcati, e da marcare
        maybe_orphan_attachments = all_orphan_attachments - confirmed_orphan_attachments

        count.update({
            'oa': len(all_orphan_attachments),
            'coa': len(confirmed_orphan_attachments),
            'poa': len(maybe_orphan_attachments)
        })

        count.update({
            'oa_mb': '{0:.2f} MiB'.format(sum(all_orphan_attachments.mapped('file_size'))/1048576),
            'coa_mb': '{0:.2f} MiB'.format(sum(confirmed_orphan_attachments.mapped('file_size'))/1048576),
            'poa_mb': '{0:.2f} MiB'.format(sum(maybe_orphan_attachments.mapped('file_size'))/1048576)
        })

        log_deleted_attachments = []
        # Esegue le operazioni
        if do_unlink:
            log_deleted_attachments = ', '.join(confirmed_orphan_attachments.mapped(lambda a: f'({a.name}, {a.checksum})'))
            confirmed_orphan_attachments.sudo().unlink()
        maybe_orphan_attachments.sudo().write({'maybe_orphan': True})
        not_orphan_attachments.sudo().write({'maybe_orphan': False})

        logger.info('ATTACHMENTS GC - DONE.')
        logger.info('ATTACHMENTS GC - Found  %d  possible orphan attachments on the active models (size %s).' % (count['oa'], count['oa_mb']))
        if do_unlink:
            logger.info('ATTACHMENTS GC - DELETED  %d  confirmed orphan attachments (size %s).' % (count['coa'], count['coa_mb']))
        else:
            logger.info('ATTACHMENTS GC - SKIPPED  %d  confirmed orphan attachments (not deleted) (size %s).' % (count['coa'], count['coa_mb']))
        logger.info('ATTACHMENTS GC - MARKED  %d  new possible orphan attachments (size %s).' % (count['poa'], count['poa_mb']))
        if do_unlink:
            logger.info('ATTACHMENTS GC - DELETED FILES  %s.' % (log_deleted_attachments or 'None'))

        # Return the logger text in order to permit to override this method
        # and log the operation with a 3rd party tool.
        log_out = stream_handler.stream.getvalue()
        return log_out

        # REMEMBER THAT...
        # Attachments left orphaned during the creation of a message/note/email
        # (while still in a transient) that eventually failed are already deleted by
        # self.env['mail.compose.message']._gc_lost_attachments(). In practice, this
        # deletes attachments with ('res_model', '=', 'mail.compose.message')
        # and ('res_id', '=', False) and created or modified at least one day before.


    # Method to be called by the overrided cron _run_vacuum_cleaner() on 'ir.autovacuum'
    def _gc_orphan_attachments_autovacuum(self):
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
            _logger.info('ATTACHMENTS GC - According to the System Parameter "%s" that is set to "%s", today this garbage collector will not be executed.' % (
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

            # Try to execute the garbage collector main method
            try:
                _logger.debug('Calling ir.attachment._garbage_collect_rel_orphan_attachments(do_unlink=%s)', str(gc_do_unlink))
                self._garbage_collect_rel_orphan_attachments(do_unlink=gc_do_unlink)
                self.env.cr.commit()
            except Exception:
                _logger.exception('Failed ir.attachemnt()._garbage_collect_rel_orphan_attachments()')
                self.env.cr.rollback()
                gc_do_unlink = False

            if gc_do_unlink:
                # Try to force execution of the filestore cleanup
                try:
                    _logger.debug('Calling ir.attachment()._gc_file_store()')
                    self.sudo()._gc_file_store()
                    self.env.cr.commit()
                except Exception:
                    _logger.exception('Failed ir.attachemnt()._gc_file_store()')
                    self.env.cr.rollback()

    # PROBLEMA IMPORTANTE DA DECIDERE COME GESTIRE:
    # @todo: Gestione file caricati in campi HTML... rischiano di essere eliminati.
    #   --> opzione in definizione modello:
    #       "elimina solo se il record collegato non esiste più"
    #       in caso di campi Html o di intenzione di usare il caricamento
    #       allegati dal chatter (quindi non deve essere nascosto).
    
    # VARIE ED EVENTUALI:
    # @todo: ?? Su registro/log degli attachment cancellati indicare anche "res_model" ??
    # @todo: ?? Implementare action multi "set as not orphan" ??
    # @todo: ?? Aggiungere constraint che dà errore se si marcano record con "res_field" != False ??
