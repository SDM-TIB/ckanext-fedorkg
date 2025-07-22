from flask import Flask, request, jsonify
from pyoxigraph import Store, RdfFormat

from . import SEMSD_PATH

app = Flask(__name__)

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
            'head': {'vars': results.variables},
            'results': {'bindings': []}
        }

        for result in results:
            binding = {}
            for var in results.variables:
                value = result.get(var)
                binding[var] = {'type': 'literal', 'value': str(value)}
            response['results']['bindings'].append(binding)

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=9000)
