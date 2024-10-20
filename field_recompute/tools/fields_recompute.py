# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

def do_fields_recompute(env, model_name, fields):
    """ Recompute the passed fields on all records
    :param env: the odoo environment;
    :param model_name: string with the model name;
    :param fields: list with the names of the fields to recompute;
    """
    model = env[model_name]
    recs = model.sudo().with_context(active_test=False).search([])
    for field in fields:
        env.add_to_compute(model._fields[field], recs)
    _logger.info('**FIELD RECOMPUTE** Recomputation STARTED for the Model [ %s ] on ALL RECORDS. Recomputed fields are : %s.' % (model_name, ', '.join(fields)))            
    env._recompute_all()
    # model.recompute()
    # env.cr.commit()
    _logger.info('**FIELD RECOMPUTE** Recomputation TERMINATED for the Model [ %s ] on ALL RECORDS. Recomputed fields are: %s.' % (model_name, ', '.join(fields)))

def do_record_fields_recompute(env, recs, fields):
    """ Recompute the passed fields on specific records
    :param env: the odoo environment;
    :param recs: recordset on which to recompute fields
    :param fields: list with the names of the fields to recompute;
    """
    if not recs:
        raise UserError('''You must specify at least one record in the "recs" argument.''')
    for field in fields:
        env.add_to_compute(recs._fields[field], recs)
    _logger.info('**FIELD RECOMPUTE** Recomputation STARTED for the Model [ %s ] on SPECIFIED RECORDS. Recomputed fields are : %s.' % (recs._name, ', '.join(fields)))            
    env._recompute_all()
    # recs.recompute()
    # env.cr.commit()
    _logger.info('**FIELD RECOMPUTE** Recomputation TERMINATED for the Model [ %s ] on SPECIFIED RECORDS. Recomputed fields are: %s.' % (recs._name, ', '.join(fields)))
