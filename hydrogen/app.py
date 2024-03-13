import re
from flask import Flask, render_template, request, jsonify
from hydrogen.search import Search

app = Flask(__name__)
es = Search()


# Hybrid using full-text and vector ranked with RRF
@app.post('/')
def handle_search():
    data = request.get_json()
    print(data)

    query = data.get('query', '')
    from_ = data.get('from_', 0)
    filters, parsed_query = extract_filters(query)

    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['name', 'summary', 'content'],
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
        knn={
            'field': 'embedding',
            'query_vector': es.get_embedding(parsed_query),
            'k': 10,
            'num_candidates': 50,
            **filters,
        },
        rank={
            'rrf': {}
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
        from_=from_,
    )
    aggs = {
        'Category': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['category-agg']['buckets']
        },
        'Year': {
            bucket['key_as_string']: bucket['doc_count']
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


# Vector KNN with filters and facets
# @app.post('/')
# def handle_search():
#     query = request.form.get('query', '')
#     filters, parsed_query = extract_filters(query)
#     from_ = request.form.get('from_', type=int, default=0)
#
#     results = es.search(
#         knn={
#             'field': 'embedding',
#             'query_vector': es.get_embedding(parsed_query),
#             'k': 10,
#             'num_candidates': 50,
#             **filters,
#         },
#         aggs={
#             'category-agg': {
#                 'terms': {
#                     'field': 'category.keyword',
#                 }
#             },
#             'year-agg': {
#                 'date_histogram': {
#                     'field': 'updated_at',
#                     'calendar_interval': 'year',
#                     'format': 'yyyy',
#                 },
#             },
#         },
#         size=5,
#         from_=from_
#     )
#     aggs = {
#         'Category': {
#             bucket['key']: bucket['doc_count']
#             for bucket in results['aggregations']['category-agg']['buckets']
#         },
#         'Year': {
#             bucket['key_as_string']: bucket['doc_count']
#             for bucket in results['aggregations']['year-agg']['buckets']
#             if bucket['doc_count'] > 0
#         },
#     }
#     return render_template('index.html', results=results['hits']['hits'],
#                            query=query, from_=from_,
#                            total=results['hits']['total']['value'], aggs=aggs)


# Full text with filters and facets
# @app.post('/')
# def handle_search():
#     query = request.form.get('query', '')
#     filters, parsed_query = extract_filters(query)
#     from_ = request.form.get('from_', type=int, default=0)
#
#     if parsed_query:
#         search_query = {
#             'must': {
#                 'multi_match': {
#                     'query': parsed_query,
#                     'fields': ['name', 'summary', 'content'],
#                 }
#             }
#         }
#     else:
#         search_query = {
#             'must': {
#                 'match_all': {}
#             }
#         }
#
#     results = es.search(
#         query={
#             'bool': {
#                 **search_query,
#                 **filters
#             }
#         },
#         aggs={
#             'category-agg': {
#                 'terms': {
#                     'field': 'category.keyword',
#                 }
#             },
#             'year-agg': {
#                 'date_histogram': {
#                     'field': 'updated_at',
#                     'calendar_interval': 'year',
#                     'format': 'yyyy',
#                 },
#             },
#         },
#         size=5,
#         from_=from_
#     )
#     aggs = {
#         'Category': {
#             bucket['key']: bucket['doc_count']
#             for bucket in results['aggregations']['category-agg']['buckets']
#         },
#         'Year': {
#             bucket['key']: bucket['doc_count']
#             for bucket in results['aggregations']['year-agg']['buckets']
#             if bucket['doc_count'] > 0
#         },
#     }
#     return render_template('index.html', results=results['hits']['hits'],
#                            query=query, from_=from_,
#                            total=results['hits']['total']['value'],
#                            aggs=aggs)


@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    if not document:
        return jsonify({'error': 'Document not found'}), 404

    title = document['_source']['title']
    nodes = document['_source']['nodes']
    edges = document['_source']['edges']

    return jsonify({
        'id': id,
        'title': title,
        'nodes': nodes,
        'edges': edges
    })


@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')


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
