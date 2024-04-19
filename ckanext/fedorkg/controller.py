
import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model

from ckan.common import request
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
        except logic.NotAuthorized:
            base.abort(403, toolkit._('Need to be system administrator to administer.'))

        from ckanext.fedorkg.views import detrusty_config
        msg = ''
        error = False
        if request.method == 'POST':
            kg = request.form.get('kg')
            action = request.form.get('action')
            if action == '0':
                # TODO: Try to delete the KG from the federation and set error state accordingly
                if error:
                    msg = toolkit._('There was an error when deleting {kg} from the federation!').format(kg=kg)
                else:
                    msg = toolkit._('Successfully removed {kg} from the federation!').format(kg=kg)
                # TODO: Remove after implementing the deletion of a KG from the federation
                error = True
                msg = 'This feature is not yet implemented.'
            elif action == '1':
                # TODO: Try to add the KG to the federation and set error state accordingly
                if error:
                    msg = toolkit._('There was an error when adding {kg} from the federation!').format(kg=kg)
                else:
                    msg = toolkit._('Successfully added {kg} from the federation!').format(kg=kg)
                error = True
                msg = 'This feature is not yet implemented.'
        return toolkit.render('admin.jinja2',
                              extra_vars={
                                  'kgs': sorted(list(detrusty_config.getEndpoints().keys())),
                                  'msg': msg,
                                  'error': error
                              })
