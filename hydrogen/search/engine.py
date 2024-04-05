from abc import ABC, abstractmethod
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from hydrogen.config import Config
import redis
import json

load_dotenv()
config = Config()
es_index_name = config.get('search_index', 'index_name')
es_index_port = config.get('search_index', 'port')
redis_host = config.get('redis', 'host')
redis_port = config.get('redis', 'port')
redis_db = config.get('redis', 'db')


class SearchImplementor(ABC):
    @abstractmethod
    def search(self, **query_args):
        pass

    @abstractmethod
    def parse_query(self, query):
        pass


class FullTextSearch(SearchImplementor):
    def __init__(self, es = None):
        self.es = es

    def parse_query(self, query):
        if query:
            return {
                'must': {
                    'multi_match': {
                        'query': query,
                        'fields': ['title', 'analyst_name', 'analyst_email', 'version'],
                    }
                }
            }
        else:
            return {
                'must': {
                    'match_all': {}
                }
            }

    def search(self, **query_args):
        return self.es.search(index=es_index_name, **query_args)


class SemanticSearch(SearchImplementor):
    def __init__(self, es = None):
        self.es = es

    def parse_query(self, query):
        if query:
            return {
                'must': {
                    'multi_match': {
                        'query': query,
                        'fields': ['title', 'analyst_name', 'analyst_email', 'version'],
                    }
                }
            }
        else:
            return {
                'must': {
                    'match_all': {}
                }
            }

    def search(self, **query_args):
        return self.es.search(index=es_index_name, **query_args)


class HybridSearch(SearchImplementor):
    def __init__(self, es = None):
        self.es = es

    def parse_query(self, query):
        if query:
            return {
                'must': {
                    'multi_match': {
                        'query': query,
                        'fields': ['title', 'analyst_name', 'analyst_email', 'version'],
                    }
                }
            }
        else:
            return {
                'must': {
                    'match_all': {}
                }
            }

    def search(self, **query_args):
        return self.es.search(index=es_index_name, **query_args)


class SearchEngine:
    def __init__(self, implementor):
        self.es = Elasticsearch('http://localhost:' + es_index_port)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.implementor = implementor(es=self.es)
        print('Connected to Elasticsearch!')

    def count_docs(self):
        return self.es.count(index=es_index_name)['count']

    def create_index(self):
        self.es.indices.delete(index=es_index_name, ignore_unavailable=True)
        self.es.indices.create(index=es_index_name)

    def reindex(self):
        self.create_index()
        chunk_list = [key.decode('utf-8') for key in self.redis.lrange('chunk_list', 0, -1)]
        for chunk in chunk_list:
            members = self.redis.smembers(chunk)
            arguments = [json.loads(member.decode('utf-8')) for member in members]
            self.insert_documents(arguments)
            print(f'{chunk} ({len(arguments)} arguments)')

    def delete_index(self):
        if self.es.indices.exists(index=es_index_name):
            response = self.es.indices.delete(index=es_index_name)
            print("Index deleted:", response)
        else:
            print("Index does not exist.")

    def retrieve_document(self, id):
        return self.es.get(index=es_index_name, id=id)

    def insert_documents(self, documents):
        operations = []
        for document in documents:
            schema = self.schema(document)
            operations.append({'index': {'_index': es_index_name}})
            operations.append({
                **schema,
            })
        return self.es.bulk(operations=operations)

    def schema(self, document):
        core_info = document['metadata']['core']
        return {
            "id": core_info['id'],
            "created": core_info['created'],
            "edited": core_info['edited'],
            "analyst_name": core_info.get('analyst_name', ''),
            "analyst_email": core_info.get('analyst_email', ''),
            "version": core_info['version'],
            "title": core_info['title'],
            "nodes": document['nodes'],
            "edges": document['edges']
        }

    def search(self, raw_query, **query_args):
        query = self.implementor.parse_query(raw_query)
        return self.implementor.search(query={'bool': query}, **query_args)
