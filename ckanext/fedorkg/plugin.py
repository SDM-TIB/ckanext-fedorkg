
from logging import getLogger

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckanext.fedorkg.helpers as helpers
import ckanext.fedorkg.views as views
from ckan.lib.plugins import DefaultTranslation

log = getLogger(__name__)


class FedORKG(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IBlueprint, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.ITranslation)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('static', 'fedorkg')
        toolkit.add_ckan_admin_tab(config_, 'fedorkg_admin.admin', 'FedORKG', icon='magnifying-glass')

    def get_blueprint(self):
        return views.get_blueprints()

    def get_helpers(self):
        return {
            'fedorkg_is_fedorkg_page': helpers.is_fedorkg_page
        }
