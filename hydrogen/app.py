from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from hydrogen.search import SearchEngine, FullTextSearch, SemanticSearch, HybridSearch
from hydrogen import Config
from hydrogen.importer import ArgsmeBatchImporter
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)
config = Config()

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
CORS(api_v1)

search_engine = SearchEngine(HybridSearch)


@api_v1.get('/search_mode')
def get_search_mode():
    if not search_engine:
        return jsonify({'message': "No search mode is set"}),

    if isinstance(search_engine.implementor, FullTextSearch):
        return jsonify('fulltext'), 200
    elif isinstance(search_engine.implementor, SemanticSearch):
        return jsonify('semantic'), 200
    elif isinstance(search_engine.implementor, HybridSearch):
        return jsonify('hybrid'), 200


@api_v1.post('/search_mode')
def set_search_mode():
    global search_engine
    body = request.get_json()
    search_mode = body.get('mode')
    if search_mode not in ['fulltext', 'semantic', 'hybrid']:
        return jsonify({'error': 'Invalid search mode'}), 400

    if search_mode == 'fulltext':
        search_engine = SearchEngine(FullTextSearch)
    elif search_mode == 'semantic':
        search_engine = SearchEngine(SemanticSearch)
    elif search_mode == 'hybrid':
        search_engine = SearchEngine(HybridSearch)

    return jsonify({'message': f'Search mode set to {search_mode}'}), 20


@api_v1.get('/count_docs')
def count_docs():
    try:
        count = search_engine.count_docs()
        return jsonify({'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v1.post('/search/fulltext')
def search_fulltext():
    if not isinstance(search_engine.implementor, FullTextSearch):
        return jsonify({'error': 'Search engine is not set to fulltext mode'}), 400

    return handle_search()


@api_v1.post('/search/hybrid')
def search_hybrid():
    if not isinstance(search_engine.implementor, HybridSearch):
        return jsonify({'error': 'Search engine is not set to hybrid mode'}), 400

    return handle_search()


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
def import_argsme():
    """
    Imports and processes the Argsme dataset: translates to 'sadface', caches in Redis.
    """
    dataset_path = os.path.join(os.getcwd(), 'datasets', 'args_me.json')

    if not os.path.exists(dataset_path):
        print(f'Dataset not found at {dataset_path}. Please ensure the file exists and try again.')
        return

    hydrogen_ascii_art = """
     _   _           _                            
    | | | |         | |                           
    | |_| |_   _  __| |_ __ ___   __ _  ___ _ __  
    |  _  | | | |/ _` | '__/ _ \ / _` |/ _ \ '_ \ 
    | | | | |_| | (_| | | | (_) | (_| |  __/ | | |
    \_| |_/\__, |\__,_|_|  \___/ \__, |\___|_| |_|
            __/ |                 __/ |           
           |___/                 |___/            
    """
    print(hydrogen_ascii_art)
    print('\n')
    print('Importing the argsme dataset...')
    argsme_importer = ArgsmeBatchImporter(dataset_path)
    argsme_importer.batch_import()

    print('\n')
    print('Try running `flask reindex` to send the data to elasticsearch!')


@app.cli.command()
def reindex():
    """
    Regenerate the Elasticsearch index
    """
    search_engine.reindex()
    print("Successfully reindexed all cached arguments")


@app.cli.command()
def del_index():
    """
    Delete the Elasticsearch index
    """
    search_engine.delete_index()
    print(f'Successfully deleted the elasticsearch index')


@app.cli.command()
def deploy_elser():
    """
    Deploy the ELSER v2 model to the Elasticsearch
    """
    if not isinstance(search_engine.implementor, HybridSearch):
        return print('Deploying ELSER only available when search mode is semantic')

    try:
        search_engine.deploy_elser()
    except Exception as exc:
        print(f'Error: {exc}')
    else:
        print(f'ELSER model deployed.')


@app.cli.command()
def generate_summary_dataset():
    """
    Generates a dataset containing [id, summary] pairs from parsed combined node texts.
    """
    search_engine.generate_summary_dataset()


app.register_blueprint(api_v1, urlprefix="/")

if __name__ == "__main__":
    app.run(port=config.get('api', 'port'), debug=True)
