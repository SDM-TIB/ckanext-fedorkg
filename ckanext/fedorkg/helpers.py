
import functools
import os

import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import requests
from ckan.common import config

LLM_API_KEY_KEY = 'ckanext.fedorkg.llm.api_key'


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


def get_api_key():
    return config.get(LLM_API_KEY_KEY, os.environ.get('OPENAI_API_KEY', ''))


def validate_model_name(model_name, api_key=get_api_key()):
    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            models = [model_['id'] for model_ in response.json()['data']]
            return model_name in models
        return False
    except:
        return False
