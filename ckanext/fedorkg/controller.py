import logging
from urllib.parse import unquote
from uuid import uuid4

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
from DeTrusty.Decomposer import Decomposer
from DeTrusty.Molecule.MTCreation import Endpoint, _accessible_endpoints
from ckan.common import request, config
from ckan.plugins import toolkit
from ckanext.fedorkg.metadata import FEDORKG_PATH, SEMSD_PATH, MetadataConfig
from ckanext.fedorkg.model.crud import NewsQuery

DEFAULT_QUERY_KEY = 'ckanext.fedorkg.query'
DEFAULT_QUERY_NAME_KEY = 'ckanext.fedorkg.query.name'
QUERY_TIMEOUT = 'ckanext.fedorkg.timeout'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class FedORKGController:

    @staticmethod
    def _check_access():
        context = {
            'model': model,
            'session': model.Session,
            'user': toolkit.c.user,
            'auth_user_obj': toolkit.c.userobj
        }
        try:
            logic.check_access('sysadmin', context, {})
        except logic.NotAuthorized:
            base.abort(403, toolkit._('Need to be system administrator to administer.'))

    @staticmethod
    def delete_kg(kg):
        FedORKGController._check_access()
        kg = unquote(kg)
        toolkit.enqueue_job(delete_kg_from_federation, [kg], title=f'Deleting {kg} from federation')
        toolkit.h.flash_notice(toolkit._('Your request has been added to the job queue. Check the FedORKG news feed for updates on the task.'))
        return h.helper_functions.redirect_to(h.url_for('fedorkg_admin.admin'))

    @staticmethod
    def add_kg():
        FedORKGController._check_access()
        kg = request.form.get('kg')
        toolkit.enqueue_job(add_kg_to_federation, [kg], title=f'Adding {kg} to federation')
        toolkit.h.flash_notice(toolkit._('Your request has been added to the job queue. Check the FedORKG news feed for updates on the task.'))
        return h.helper_functions.redirect_to(h.url_for('fedorkg_admin.admin'))

    @staticmethod
    def admin():
        FedORKGController._check_access()

        error = False
        if request.method == 'POST':
            action = request.form.get('action', None)
            if action == 'default_query':
                query = request.form.get(DEFAULT_QUERY_KEY, '').strip().replace('\r\n', '\n')
                query_name = request.form.get(DEFAULT_QUERY_NAME_KEY, '').strip()
                if query != '' and query_name != '':
                    decomposed_query = None
                    try:
                        decomposed_query = Decomposer(query, MetadataConfig()).decompose()
                    except:
                        error = True
                        toolkit.h.flash_error(toolkit._('The query is malformed. Please, check your syntax.'))

                    if not error:
                        if decomposed_query is None:
                            toolkit.h.flash_error(toolkit._('The query cannot be answer by the federation of FedORKG.'))
                        else:
                            logic.get_action(u'config_option_update')({
                                u'user': toolkit.c.user
                            }, {
                                DEFAULT_QUERY_KEY: query.replace('\n', '\\n'),
                                DEFAULT_QUERY_NAME_KEY: query_name
                            })
                            toolkit.h.flash_success(toolkit._('The default query has been updated successfully.'))
                else:
                    toolkit.h.flash_error(toolkit._('The default query and its name are required.'))
            elif action == 'query_timeout':
                timeout = request.form.get(QUERY_TIMEOUT, '')
                try:
                    timeout = int(timeout)
                except ValueError:
                    error = True
                    toolkit.h.flash_error(toolkit._('The query timeout is specified in full seconds. Please, provide input that can be parsed as an integer.'))

                if not error:
                    logic.get_action(u'config_option_update')({
                        u'user': toolkit.c.user
                    }, {
                        QUERY_TIMEOUT: timeout
                    })
                    toolkit.h.flash_success(toolkit._('New query timeout set successfully.'))

        return toolkit.render('admin_fedorkg.jinja2',
                              extra_vars={
                                  'query': config.get(DEFAULT_QUERY_KEY).strip().replace('\\n', '\n'),
                                  'query_name': config.get(DEFAULT_QUERY_NAME_KEY).strip().replace('\\n', '\n'),
                                  'timeout': config.get(QUERY_TIMEOUT),
                                  'kgs': sorted(list(MetadataConfig().getEndpoints().keys())),
                                  'fedorkg_news': NewsQuery.read_all_news()
                              })


def add_kg_to_federation(kg):
    NewsQuery.create(uuid4(), kg, 'notice', toolkit._('Starting to add the endpoint.'))
    error = False
    msg = toolkit._('Added the endpoint successfully.')
    endpoint = Endpoint(kg)
    accessible = endpoint in _accessible_endpoints([endpoint])
    if accessible:
        try:
            metadata = MetadataConfig()
            metadata.add_endpoint(kg)
            metadata.saveToFile(SEMSD_PATH)
        except Exception as e:
            error = True
            logger.exception(e)
            msg = toolkit._('Exception while adding! {exc_type} {exc_args}').format(
                exc_type=type(e).__name__,
                exc_args=e.args
            )
    else:
        error = True
        msg = toolkit._('The endpoint is not accessible and, hence, cannot be added to the federation.')

    NewsQuery.create(uuid4(), kg, 'error' if error else 'success', msg)


def delete_kg_from_federation(kg):
    NewsQuery.create(uuid4(), kg, 'notice', toolkit._('Starting to delete the endpoint.'))
    error = False
    msg = toolkit._('Removed the endpoint successfully.')
    try:
        metadata = MetadataConfig()
        metadata.delete_endpoint(kg)
        metadata.saveToFile(SEMSD_PATH)
    except Exception as e:
        error = True
        logger.exception(e)
        msg = toolkit._('Exception while removing! {exc_type} {exc_args}').format(
            exc_type=type(e).__name__,
            exc_args=e.args
        )

    NewsQuery.create(uuid4(), kg, 'error' if error else 'success', msg)
