import logging

from flask import Flask, request, jsonify
from pyoxigraph import Store, RdfFormat, Literal

from . import SEMSD_PATH

app = Flask(__name__)
logger = logging.getLogger(__name__)

store = Store()
with open(SEMSD_PATH, 'r') as file:
    ttl = file.read()
    store.bulk_load(ttl, format=RdfFormat.TURTLE)


@app.route('/')
def index():
    return 'Metadata KG'


@app.route('/sparql', methods=['GET', 'POST'])
def sparql_endpoint():
    # Extract the SPARQL query from the request (GET or POST)
    if request.method == 'POST':
        query = request.form.get('query')
    else:
        query = request.args.get('query')

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Execute the SPARQL query
        results = store.query(query)

        # Format results into a JSON-friendly structure
        response = {
            'head': {'vars': [var.value for var in results.variables]},
            'results': {'bindings': []}
        }

        for result in results:
            binding = {}
            for var in results.variables:
                if result[var]:
                    value = result[var].value
                    if not isinstance(result[var], Literal):
                        binding[str(var.value)] = {'type': 'uri', 'value': value}
                    else:
                        if result[var].datatype is not None:
                            binding[str(var.value)] = {'type': 'typed-literal', 'value': value, 'datatype': result[var].datatype.value}
                        else:
                            binding[str(var.value)] = {'type': 'literal', 'value': value}
            response['results']['bindings'].append(binding)

        return jsonify(response)

    except Exception as e:
        logger.exception(e)
        return jsonify({'error': str(e)}), 500


@app.route('/sparql-update', methods=['POST'])
def update():
    query = request.data.decode()

    if not query:
        return jsonify({'error': 'No update query provided'}), 400

    try:
        store.update(query)
        return 'success'
    except Exception as e:
        logger.exception(e)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=9000)
