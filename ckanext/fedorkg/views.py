
from DeTrusty import run_query
from DeTrusty.Molecule.MTManager import get_config
from flask import Blueprint, render_template, jsonify, request

fedorkg = Blueprint('fedorkg', __name__, url_prefix='/fedorkg')


def query_editor():
    return render_template('sparql.jinja2')


def sparql():
    query = request.values.get('query', None)
    if query is None:
        return jsonify({"result": [], "error": "No query passed."})
    yasqe = request.values.get('yasqe', False)
    return jsonify(
        run_query(
            query=query,
            config=get_config('/DeTrusty/Config/rdfmts.json'),
            join_stars_locally=False,
            yasqe=yasqe
        )
    )


fedorkg.add_url_rule('/sparql', view_func=query_editor, methods=['GET'])
fedorkg.add_url_rule('/sparql', view_func=sparql, methods=['POST'])


def get_blueprints():
    return [fedorkg]
