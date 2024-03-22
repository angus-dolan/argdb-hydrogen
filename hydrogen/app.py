import re
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS, cross_origin
from hydrogen.search import Search
from hydrogen import Config

app = Flask(__name__)
es = Search()
config = Config()

CORS(app, resources={r'/*': {'origins': 'http://localhost:3000'}})
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1.route('/count_docs', methods=['GET'])
def count_docs():
    try:
        doc_count = es.count_docs()
        return jsonify({'count': doc_count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v1.post('')
def handle_search():
    body = request.get_json()
    query = body.get('query')
    filters, parsed_query = extract_filters(query)
    from_ = body.get('from_', 0)

    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['title', 'analyst_name', 'analyst_email', 'version'],
                }
            }
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }

    results = es.search(
        query={
            'bool': {
                **search_query,
                **filters
            }
        },
        aggs={
            'category-agg': {
                'terms': {
                    'field': 'category.keyword',
                }
            },
            'year-agg': {
                'date_histogram': {
                    'field': 'updated_at',
                    'calendar_interval': 'year',
                    'format': 'yyyy',
                },
            },
        },
        size=5,
        from_=from_
    )
    aggs = {
        'Category': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['category-agg']['buckets']
        },
        'Year': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['year-agg']['buckets']
            if bucket['doc_count'] > 0
        },
    }

    return jsonify({
        'results': results['hits']['hits'],
        'query': query,
        'from': from_,
        'total': results['hits']['total']['value'],
        'aggs': aggs
    })


@api_v1.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)

    if not document:
        return jsonify({'error': 'Document not found'}), 404

    return jsonify(document['_source'])


@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print("Successfully processed and indexed all batches")


@app.cli.command()
def delindex():
    """Delete the Elasticsearch index."""
    response = es.delete_index()
    print(f'Index destroyed')


def extract_filters(query):
    filters = []

    filter_regex = r'category:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'category.keyword': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    filter_regex = r'year:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'range': {
                'updated_at': {
                    'gte': f'{m.group(1)}||/y',
                    'lte': f'{m.group(1)}||/y',
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query


app.register_blueprint(api_v1)

if __name__ == "__main__":
    app.run(port=config.get('api', 'port'), debug=True)
