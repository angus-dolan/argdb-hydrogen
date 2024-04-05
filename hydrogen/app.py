import re
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS, cross_origin
from hydrogen.search import SearchEngine, FullTextSearch
from hydrogen import Config

app = Flask(__name__)
search_engine = SearchEngine(FullTextSearch)
config = Config()

cors = CORS()
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1.get('/count_docs')
def count_docs():
    try:
        count = search_engine.count_docs()
        return jsonify({'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v1.post('')
def handle_search():
    body = request.get_json()
    query = body.get('query')
    from_ = body.get('from_', 0)

    results = search_engine.search(query, size=5, from_=from_)

    return jsonify({
        'results': results['hits']['hits'],
        'query': query,
        'from': from_,
        'total': results['hits']['total']['value']
    })


@api_v1.get('/document/<id>')
def get_document(id):
    document = search_engine.retrieve_document(id)

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    return jsonify(document['_source'])


@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    search_engine.reindex()
    print("Successfully reindexed all cached arguments")


@app.cli.command()
def delindex():
    """Delete the Elasticsearch index."""
    search_engine.delete_index()
    print(f'Successfully deleted the elasticsearch index')


app.register_blueprint(api_v1, urlprefix="/")
cors.init_app(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*", "supports_credentials": True}})

if __name__ == "__main__":
    app.run(port=config.get('api', 'port'), debug=True)
