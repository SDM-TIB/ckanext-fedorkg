
import functools
import os

import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import requests


def icon():
    if toolkit.check_ckan_version(min_version='2.10'):
        return 'magnifying-glass'
    else:
        return 'search'


def require_access(action_name):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            context = {
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


def validate_model_name(model_name):
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            models = [model_['id'] for model_ in response.json()['data']]
            return model_name in models
        return False
    except:
        return False
