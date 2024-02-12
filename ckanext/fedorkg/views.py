
from flask import Blueprint

fedorkg = Blueprint('fedorkg', __name__)


def sparql():
    return 'Hello, this is FedORKG!'


fedorkg.add_url_rule('/fedorkg/sparql', view_func=sparql)


def get_blueprints():
    return [fedorkg]
