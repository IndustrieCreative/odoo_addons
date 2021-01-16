# -*- coding: utf-8 -*-

import logging
from odoo import fields, models
from odoo.tools.profiler import profile

_logger = logging.getLogger(__name__)

CG_MODULE_BLACKLIST = [
    'ir.ui.view',
]

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    maybe_orphan = fields.Boolean(
        string = 'Maybe orphan?',
        readonly = True,
        help = '''"True" if this attachment was found to be orphaned during the last check.
            If the attachment is found to be orphaned during the next check as well, it will be deleted.
            Otherwise this flag will be removed.'''
    )

    # @todo: ?? Aggiungere constraint che dà errore se si marcano record con "res_id" != False ??

    '''
       Elimina tutti gli attachment rimasti orfani dopo che la relazione con un 
       determinato modello è stata interrotta a causa dell'eliminazione del record
       oppure per la modifica del campo che puntava all'attachment. Questo problema
       si presenta in particolar modo utilizzando il widget "many2many_binary".
       Il garbage collector si attiva solo nei modelli in cui esiste un
       attributo "_attachment_garbage_collector" impostato a True.

       ATTENZIONE:
       Gestisce solo campi Many2any e Many2one che puntano a "ir.attachment"
       e con dominio [('res_model', '=', _name)]. In altre parole, se attivi la
       funzione su un modulo, non dovresti puntare ad attachment il cui "res_model"
       non sia il modulo stesso.
       
       Per i campi Many2many si presume di usare il widget "many2many_binary"
       il quale si occupa di gestire correttamente il dominio degli attachment
       visualizzati e i valori di default di quelli creati (soprattutto "res_model").

       Con i campi Many2one si può aggiungere eventualmente la condizione
       [('res_id', '=', id)] al dominio precedente (il quale resta imprescindibile);
       in questo caso è necessario ereditare il 'mail.thread' mixin il quale si occuperà
       lui di gestire/eliminare nel modo corretto gli attachment con [('res_id', '!=', 0)].

       Alcuni modelli hanno una gestione degli attachment non standard e possono
       verificarsi effetti inattesi se questo garbage collector viene attivato su
       di essi. In questo caso basta aggiungere il nome dei modelli da ignorare
       al dict CG_MODULE_BLACKLIST per evitare un'attivazione erronea su di essi.

       La prima volta che individua degli attachment orfani li marchia solo.
       La seconda volta che viene eseguito questo metodo, se trova che sono gli stessi,
       li elimina (questo per ridurre possibili errori quando il numero di attachment
       sarà molto grande). Quelli marchiati che non risultano più orfani,
       vengono de-marchiati

    '''
    @profile
    def _garbage_collect_rel_orphan_attachments(self):
        active_models = []
        # Ottiene tutti i modelli registrati dall'ORM
        all_models = self.env['ir.model'].sudo().search([])
        # Per ciascun modello
        for model in all_models:
            model_name = model.model
            try:
                Model = self.env[model_name]
            except KeyError:
                _logger.warning('ATTACHMENTS GARBAGE COLLECTOR: The model "%s" is present in "ir.model" but no longer exists in the environment.' % model_name)
                continue
            # Se il modello ha l'attibuto '_attachment_garbage_collector' impostato su True
            if getattr(Model, '_attachment_garbage_collector', False) == True:
                # Ignora i modelli nella blacklist
                if model_name in CG_MODULE_BLACKLIST:
                    _logger.warning('ATTACHMENTS GARBAGE COLLECTOR: The model "%s" cannot have the "_attachment_garbage_collector" attribute set to True. The attriburte has been ignored.' % model_name)
                    continue
                # Trova tutti i campi many2many e many2one del modello che puntano a 'ir.attachment'
                fields_dict = Model.fields_get([], ['type', 'relation'])
                m2m_attachment_fields = []
                m2o_attachment_fields = []
                for field_name, field_attrs in fields_dict.items():
                    if field_attrs.get('type') == 'many2many' and field_attrs.get('relation') == 'ir.attachment':
                        model_field = Model._fields.get(field_name)
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
                active_models.append({
                    'model_name': model_name,
                    'm2m_attachment_fields': m2m_attachment_fields,
                    'm2o_attachment_fields': m2o_attachment_fields
                })
            else:
                continue

        used_attachments = self.env['ir.attachment'] # empty recordset

        # Tutti gli attachment associati ai modelli "attivi" e senza "res_id"
        model_names = [model['model_name'] for model in active_models]
        all_active_models_attachments = self.env['ir.attachment'].sudo().with_context(active_test=False).search([
            '&',
                ('res_model', 'in', model_names),
                '|', # Così non tocca gli attachment dei messaggi nel chatter
                    ('res_id', '=', 0),
                    ('res_id', '=', False)
        ])

        # Trova tutti gli attachment usati da record dei modelli "attivi"
        for model in active_models:
            Model = self.env[model['model_name']]
            # model_all_records = Model.sudo().with_context(active_test=False).search([])

            for res_m2m_field in model['m2m_attachment_fields']:
                
                # MODO 1
                # m2m_field_used_attachments = model_all_records.mapped(res_m2m_field['name'])
                #----------- 
                
                # MODO 2
                self.env.cr.execute('SELECT %s FROM %s' % (res_m2m_field['column2'], res_m2m_field['relation']))
                m2m_field_used_attachments_ids = [id[0] for id in self.env.cr.fetchall()]
                m2m_field_used_attachments = self.env['ir.attachment'].sudo().browse(m2m_field_used_attachments_ids)
                #----------- 

                used_attachments |= m2m_field_used_attachments

            for res_m2o_field in model['m2o_attachment_fields']:
                
                # MODO 1
                # m2o_field_used_attachments = model_all_records.mapped(res_m2o_field['name'])
                #----------- 

                # MODO 2
                m2o_field_used_attachments = Model.sudo().with_context(active_test=False).search([
                    (res_m2o_field['name'], '!=', False)
                ]).mapped(res_m2o_field['name'])
                #----------- 
                
                used_attachments |= m2o_field_used_attachments


        # Individua gli attachment orfani
        orphan_attachments = all_active_models_attachments - used_attachments

        # Gli attachment che sono stati marcati precedentemente, ma ora non risultano più orfani
        not_orphan_attachments = used_attachments.filtered('maybe_orphan')
        # Gli attachment che erano già marcati
        confirmed_orphan_attachments = orphan_attachments.filtered('maybe_orphan')
        # Gli attachment non ancora marcati, e da marcare
        maybe_orphan_attachments = orphan_attachments - confirmed_orphan_attachments

        # Esegue le operazioni
        confirmed_orphan_attachments.sudo().unlink()
        maybe_orphan_attachments.sudo().write({'maybe_orphan': True})
        not_orphan_attachments.sudo().write({'maybe_orphan': False})

        # orphan_attachments.sudo().unlink()

        # <!> Già fatto da '_garbage_collect_attachments()' @ 'mail.thread'
        # self._clean_orphan_compose_message_attachments()


    # <!> Già fatto da '_garbage_collect_attachments()' @ 'mail.thread'
    # # Elimina gli attachment rimasti orfani durante la creazione di un messaggio/nota/email
    # # quando è ancora in un transient e che non è andato a buon fine
    # def _clean_orphan_compose_message_attachments(self):
    #     wizard_attachments = self.sudo().with_context(active_test=False).search([
    #         ('res_model', '=', 'mail.compose.message'),
    #         ('create_date', '<=', fields.Datetime.now()-timedelta(hours=12)) # Così non elimina l'attachment mentre un utente sta scrivendo un messaggio
    #     ])
    #     wizard_attachments.sudo().unlink()
