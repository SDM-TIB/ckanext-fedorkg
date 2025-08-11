
import os
from typing import Any, cast

import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model
import requests
from DeTrusty import __version__ as detrusty_version
from DeTrusty import run_query
from ckan.common import request, config
from ckan.plugins import toolkit
from ckan.types import Context
from ckan.views.user import _extra_template_variables
from ckanext.fedorkg import __version__ as fedorkg_version
from ckanext.fedorkg.controller import FedORKGController, DEFAULT_QUERY_KEY, DEFAULT_QUERY_NAME_KEY, QUERY_TIMEOUT
from ckanext.fedorkg.metadata import FEDORKG_PATH, MetadataConfig
from ckanext.fedorkg.model.crud import NewsQuery
from flask import Blueprint, jsonify, request

fedorkg = Blueprint('fedorkg', __name__, url_prefix='/fedorkg')
admin_bp = Blueprint('fedorkg_admin', __name__ + '_admin', url_prefix='/ckan-admin')


def init_prompt():
    with open(os.path.join(FEDORKG_PATH, 'prompt.txt'), 'r', encoding='utf-8') as prompt_file:
        return prompt_file.read()


prompt = init_prompt()


def query_editor():
    if toolkit.check_ckan_version(min_version='2.10'):
        margin = '-0.75rem'
    else:
        margin = '-15px'
    return toolkit.render('sparql.jinja2',
                          extra_vars={
                              'detrusty_version': detrusty_version,
                              'fedorkg_version': fedorkg_version,
                              'default_query': config.get(DEFAULT_QUERY_KEY, ''),
                              'default_query_name': config.get(DEFAULT_QUERY_NAME_KEY, ''),
                              'margin': margin,
                              'timeout': config.get(QUERY_TIMEOUT)
                          })


def sparql():
    query = request.values.get('query', None)
    if query is None:
        return jsonify({"result": [], "error": "No query passed."})
    yasqe = request.values.get('yasqe', False)
    return jsonify(
        run_query(
            query=query,
            config=MetadataConfig(),
            join_stars_locally=False,
            yasqe=yasqe,
            timeout=int(config.get(QUERY_TIMEOUT))
        )
    )


def llm():
    question = request.values.get('question', None)
    if question is None:
        raise ValueError('ERROR: No question passed.')
    elif len(question) > 128:
        raise ValueError('ERROR: Your question exceeds 128 characters.')
    else:
        api_key = os.environ.get('OPENAI_API_KEY', None)
        if api_key is None:
            raise ValueError('ERROR: Missing OpenAI API key.')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        data = {
            "model": "o1-mini",
            "messages": [
                {"role": "user", "content": f"{prompt}\n{question}"}
            ]
        }

        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad status codes

            content = response.json()['choices'][0]['message']['content']
            return content

        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise RuntimeError(f"An error occurred: {err}")


def news():
    if request.method == 'POST':
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

        news_id = request.form.get('news_id', None)
        if news_id is not None:
            NewsQuery.delete_news(news_id)

    context = cast(Context, {
        u'for_view': True,
        u'user': toolkit.current_user.name,
        u'auth_user_obj': toolkit.current_user
    })
    data_dict: dict[str, Any] = {
        u'user_obj': toolkit.current_user,
        u'include_datasets': True}
    extra_vars = _extra_template_variables(context, data_dict)
    extra_vars['fedorkg_news'] = NewsQuery.read_all_news()
    return toolkit.render('user/dashboard_fedorkg.html', extra_vars)


fedorkg.add_url_rule('/sparql', view_func=query_editor, methods=['GET'])
fedorkg.add_url_rule('/sparql', view_func=sparql, methods=['POST'])
fedorkg.add_url_rule('/llm', view_func=llm, methods=['POST'])
admin_bp.add_url_rule('/fedorkg', view_func=FedORKGController.admin, methods=['GET', 'POST'])
admin_bp.add_url_rule('/fedorkg/delete_kg/<kg>', view_func=FedORKGController.delete_kg, methods=['POST'])
admin_bp.add_url_rule('/fedorkg/add_kg', view_func=FedORKGController.add_kg, methods=['POST'])


def get_blueprints():
    from ckan.views.dashboard import dashboard
    dashboard.add_url_rule('/fedorkg', view_func=news, methods=['GET', 'POST'])
    return [fedorkg, admin_bp, dashboard]
