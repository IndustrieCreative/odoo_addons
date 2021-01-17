# -*- coding: utf-8 -*-

import logging
from odoo import fields, models
from odoo.tools.profiler import profile

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    CG_MODULE_NAME_BLACKLIST = []
    CG_MODULE_PREFIX_BLACKLIST = ['ir.']

    maybe_orphan = fields.Boolean(
        readonly = True,
        string = 'Maybe orphan?',
        help = '''"True" if this attachment was found to be orphaned during the last check
            by _garbage_collect_rel_orphan_attachments(). If the attachment is found to be
            orphaned during the next check as well, it will be deleted. Otherwise this flag
            will be removed.'''
    )

    # @todo: ?? Aggiungere constraint che dà errore se si marcano record con "res_id" != False ??

    # @todo: Possibilità di eseguirlo manualmente solo su un modello senza che questo sia attivo,
    #        passando il nome del modello come argomento. Ovviamente bisogna eseguirlo due volte per
    #        eliminare definitivemente gli attachemnt. Eseguendolo maualmente però i file fisici
    #        saranno eliminati al prossimo vacuum cron (power_on).
    #        Magari aggiungere il pulsante all'action nel form view di "ir.model".
    #        Se eseguiita manualmente, mostra info ad-hoc nel log.

    # @todo: Implementare registro/log degli attachment cancellati (hash, tipo, dimensione, res_name, res_model)

    # @todo: Implementare l'esecuzione solo un giorno alla settimana (es. domenica)

    # @todo: Implementare action multi "set as not orphan"

    '''
       Nei modelli in cui la funzionalità è attiva, elimina tutti gli attachment rimasti orfani
       dopo che tutte le relazioni (con qualunque altro modello nell'environment) sono
       state interrotte a causa dell'eliminazione dei record oppure per la modifica dei campi
       che puntavano all'attachment. Questo problema si presenta in particolar modo utilizzando
       il widget "many2many_binary".
       
       Questo garbage collector elimina solo gli attachment con i campi "res_id" vuoto e "res_model"
       che punta ad un modello il cui attributo "_attachment_garbage_collector" impostato a True.

       ATTENZIONE:
       Gestisce solo campi Many2any e Many2one che puntano a record in "ir.attachment"
       e con dominio [('res_model', '=', _name)]. In altre parole, se attivi la
       funzione su un modulo e vuoi che elimini TUTTI gli attachment rimesti orfani,
       non dovresti puntare ad attachment il cui "res_model" non sia anche esso un modulo
       con  "_attachment_garbage_collector" impostato a True.
       
       Per i campi Many2many si presume di usare il widget "many2many_binary"
       il quale si occupa di gestire correttamente il dominio degli attachment
       visualizzati e i valori di default di quelli creati (soprattutto "res_model").

       Con i campi Many2one si può aggiungere eventualmente la condizione
       [('res_id', '=', id)] al dominio precedente (il quale resta imprescindibile);
       in questo caso è necessario ereditare il 'mail.thread' mixin il quale si occuperà
       lui di gestire/eliminare nel modo corretto gli attachment con [('res_id', '!=', 0)].

       Alcuni modelli hanno una gestione degli attachment non standard e potrebbero
       verificarsi effetti inattesi se questo garbage collector venisse attivato su
       di essi. In questo caso basta aggiungere il nome dei modelli da ignorare
       al dict CG_MODULE_NAME_BLACKLIST per evitare un'attivazione erronea su di essi.
       Es. self.env['ir.attachment'].CG_MODULE_NAME_BLACKLIST.append('model.to.add')

       La prima volta che individua degli attachment orfani li marchia solo (campo
       "maybe_orphan"). La seconda volta che questo metodo viene eseguito, se trova che
       sono gli stessi, li elimina (questo per ridurre possibili errori quando il numero
       di attachment sarà molto grande).
       Quelli marchiati precedentemente e che non risultano più orfani, vengono de-marchiati.

    '''

    # @profile
    def _garbage_collect_rel_orphan_attachments(self):
        count = {'model': 0, 'm2m': 0, 'm2o': 0}

        # Prepara la blacklist effettiva
        cg_name_blacklist = [ model_name
            for model_name in self.env if model_name[0:3] in self.CG_MODULE_PREFIX_BLACKLIST
        ]
        cg_name_blacklist = list(set(cg_name_blacklist + self.CG_MODULE_NAME_BLACKLIST))
        _logger.info('ATTACHMENTS GARBAGE COLLECTOR - The model blackist is: %s' % ', '.join(cg_name_blacklist))

        # Tutti i modelli che hanno campi Many2many o Many2one che puntano a "ir.attachemnt"
        rel_models = []
        # Tutti i modellli attivi
        act_models = []
        for model_name in self.env:
            Model = self.env[model_name]
            if not Model._abstract:
                # Trova tutti i campi many2many e many2one del modello che puntano a 'ir.attachment'
                m2m_attachment_fields = []
                m2o_attachment_fields = []
                fields_dict = Model.fields_get([], ['type', 'relation', 'store'])
                for field_name, field_attrs in fields_dict.items():
                    model_field = Model._fields.get(field_name)
                    if field_attrs.get('store') and not model_field.inherited:
                        if field_attrs.get('type') == 'many2many' and field_attrs.get('relation') == 'ir.attachment':
                            m2m_attachment_fields.append({
                                'name': field_name,
                                'relation': model_field.relation,
                                'column1': model_field.column1,
                                'column2': model_field.column2
                            })
                            count['m2m'] += 1
                        elif field_attrs.get('type') == 'many2one' and field_attrs.get('relation') == 'ir.attachment':
                            m2o_attachment_fields.append({
                                'name': field_name
                            })
                            count['m2o'] += 1
                        else:
                            continue
                    else:
                        continue
            else:
                continue

            # Legge l'attributo che attiva il gc sul modello
            is_active_model = getattr(Model, '_attachment_garbage_collector', False)
            # Valida il tipo dell'attributo
            if type(is_active_model) is not bool:
                is_active_model = False
                _logger.warning('ATTACHMENTS GARBAGE COLLECTOR - The "_attachment_garbage_collector" attribute of the model "%s" is not boolean. The attriburte has been ignored.' % model_name)
            # Ignora come attivi i modelli nella blacklist
            if is_active_model and (model_name in cg_name_blacklist):
                is_active_model = False
                _logger.warning('ATTACHMENTS GARBAGE COLLECTOR - The model "%s" cannot have the "_attachment_garbage_collector" attribute set to True. The attriburte has been ignored.' % model_name)

            # Se punta a "ir.attachment" o è un modello attivo
            if m2m_attachment_fields or m2o_attachment_fields:
                rel_models.append({
                    'model_name': model_name,
                    'm2m_attachment_fields': m2m_attachment_fields,
                    'm2o_attachment_fields': m2o_attachment_fields
                })
                count['model'] += 1
            if is_active_model:
                act_models.append(model_name)

        _logger.info('ATTACHMENTS GARBAGE COLLECTOR -  %d  Many2many and  %d  Many2one fields related to "ir.attachment" were found on  %d  different models.' % (count['m2m'], count['m2o'], count['model']))

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
        
        _logger.info('ATTACHMENTS GARBAGE COLLECTOR - The service is active this  %d  models: %s' % (len(act_models), ', '.join(act_models)))
        _logger.info('ATTACHMENTS GARBAGE COLLECTOR - In the active models,  %d  attachments were found which need to be checked.' % len(all_active_models_attachments))

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
        confirmed_orphan_attachments.sudo().unlink()
        maybe_orphan_attachments.sudo().write({'maybe_orphan': True})
        not_orphan_attachments.sudo().write({'maybe_orphan': False})

        _logger.info('ATTACHMENTS GARBAGE COLLECTOR - DONE')
        _logger.info('                              - Found  %d  possible orphan attachments on the active model/s.' % count['oa'])
        _logger.info('                              -        %d  confirmed orphan attachments will be DELETED.' % count['coa'])
        _logger.info('                              -        %d  new possible orphan attachments will be MARKED.' % count['poa'])

        # NB:
        # Gli attachment rimasti orfani durante la creazione di un messaggio/nota/email
        # (quando è ancora in un transient) che alla fine non è andata a buon fine,
        # sono già eliminati da self.emv['mail.thread']._garbage_collect_attachments()
        # In pratica elimina gli attachment con('res_model', '=', 'mail.compose.message')
        # creati o modificati al minimo un giorno prima.
