
from flask import Blueprint, render_template

fedorkg = Blueprint('fedorkg', __name__, url_prefix='/fedorkg')


def sparql():
    return render_template('sparql.jinja2')


fedorkg.add_url_rule('/sparql', view_func=sparql)


def get_blueprints():
    return [fedorkg]
