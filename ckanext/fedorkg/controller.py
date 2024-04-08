
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model

from ckan.plugins import toolkit


class FedORKGController:

    @staticmethod
    def admin():
        context = {
            'model': model,
            'session': model.Session,
            'user': toolkit.c.user,
            'auth_user_obj': toolkit.c.userobj
        }
        try:
            logic.check_access('sysadmin', context, {})
            from ckanext.fedorkg.views import detrusty_config
            return toolkit.render('admin.jinja2',
                                  extra_vars={'kgs': sorted(list(detrusty_config.getEndpoints().keys()))})
        except logic.NotAuthorized:
            base.abort(403, 'Need to be system administrator to administer.')
