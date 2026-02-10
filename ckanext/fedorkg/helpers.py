
import functools

import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.types import Context


def is_fedorkg_page():
    # exclude the admin and dashboard page
    return False if 'ckan-admin' in h.current_url() else '/fedorkg' in h.current_url()


def icon():
    if toolkit.check_ckan_version(min_version='2.10'):
        return 'magnifying-glass'
    else:
        return 'search'


def require_access(action_name):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            context: Context = {
                'model': model,
                'session': model.Session,
                'user': toolkit.c.user,
                'auth_user_obj': toolkit.c.userobj
            }
            try:
                toolkit.check_access(action_name, context)
            except logic.NotAuthorized:
                base.abort(403, toolkit._('Need to be system administrator to administer.'))
            return fn(*args, **kwargs)
        return wrapper
    return deco
