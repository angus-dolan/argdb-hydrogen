from abc import ABC, abstractmethod
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from hydrogen.config import Config
from hydrogen.search.language.punctuation import punctuation_list
from hydrogen.search.language.stopwords import stopwords_list
from sentence_transformers import SentenceTransformer
import redis
import json
import time
import os
import re

load_dotenv()
config = Config()
search_mode = config.get('search', 'mode')
hybrid_inference = config.get('search', 'hybrid_inference')
es_index_name = config.get('search', 'index_name')
es_index_port = config.get('search', 'port')
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
    def __init__(self, es=None):
        self.es = es

    def parse_query(self, query):
        if query:
            return {
                'query': {
                    'bool': {
                        'must': {
                            'multi_match': {
                                'query': query,
                                'fields': ['title', 'analyst_name', 'analyst_email', 'version'],
                            }
                        }
                    }
                }
            }
        else:
            return {
                'query': {
                    'match_all': {}
                }
            }

    def search(self, **query_args):
        return self.es.search(index=es_index_name, body=query_args)

    def create_index(self):
        self.es.indices.delete(index=es_index_name, ignore_unavailable=True)
        self.es.indices.create(index=es_index_name)


class HybridSearch(SearchImplementor):
    def __init__(self, es=None):
        self.es = es
        self.embeddings = self.retrieve_embeddings()

    def retrieve_embeddings(self):
        file_path = os.path.join(os.getcwd(), 'datasets', 'embeddings_dataset.json')

        if not os.path.exists(file_path):
            os.remove(file_path)
            print(f"embeddings dataset is not present in datasets directory")

        embeddings = {}
        with open(f'{file_path}', 'r') as file:
            data = json.load(file)
            for embedding in data:
                embeddings[embedding['id']] = embedding['embedding']
        return embeddings

    def parse_query(self, query):
        if query:
            return {
                'query': {
                    'bool': {
                        'must': {
                            'multi_match': {
                                'query': query,
                                'fields': ['title', 'analyst_name', 'analyst_email', 'version'],
                            }
                        }
                    }
                }
            }
        else:
            return {
                'query': {
                    'match_all': {}
                }
            }

    def search(self, **query_args):
        return self.es.search(index=es_index_name, body=query_args)

    def create_index(self):
        self.es.indices.delete(index=es_index_name, ignore_unavailable=True)
        self.es.indices.create(index=es_index_name, mappings={
            'properties': {
                'embedding': {
                    'type': 'dense_vector',
                }
            }
        })

    def get_embedding(self, _id):
        return self.embeddings.get(_id, None)


class SemanticSearch(SearchImplementor):
    def __init__(self, es=None):
        self.es = es

    def parse_query(self, query):
        if query:
            return {
                'query': {
                    'text_expansion': {
                        'elser_embedding': {
                            'model_id': '.elser_model_2',
                            'model_text': query,
                        }
                    }
                }
            }
        else:
            return {
                'query': {
                    'match_all': {}
                }
            }

    def search(self, **query_args):
        return self.es.search(index=es_index_name, body=query_args)

    def create_index(self):
        self.es.indices.delete(index=es_index_name, ignore=[404])
        self.es.indices.create(index=es_index_name, body={
            "mappings": {
                # "dynamic": True,
                "properties": {
                    "elser_embedding": {
                        "type": "sparse_vector"
                    },
                }
            },
            "settings": {
                "index": {
                    "default_pipeline": "elser-ingest-pipeline"
                }
            }
        })

    def deploy(self):
        model_id = '.elser_model_2'

        # Remove existing deployment
        try:
            # Attempt to stop existing model deployment (if it exists)
            self.es.ml.stop_trained_model_deployment(model_id=model_id, force=True)
            print(f"Model {model_id} undeployed successfully.")
        except Exception as e:
            # Handle exception if the model isn't deployed
            print(f"No existing deployment to undeploy for model {model_id}: {e}")

        # Download model
        self.es.ml.put_trained_model(model_id=model_id, input={'field_names': ['text_field']})

        # Wait until ready
        while True:
            status = self.es.ml.get_trained_models(model_id=model_id, include='definition_status')
            if status['trained_model_configs'][0]['fully_defined']:
                break  # Model is ready
            time.sleep(1)

        # Deploy the model
        # https://www.elastic.co/guide/en/elasticsearch/reference/8.3/start-trained-model-deployment.html
        self.es.ml.start_trained_model_deployment(
            model_id=model_id,
            queue_capacity=100000,
            threads_per_allocation=4,
        )

        # Define a pipeline
        self.es.ingest.put_pipeline(
            id='elser-ingest-pipeline',
            error_trace=True,
            # timeout='60s',
            processors=[
                {
                    'inference': {
                        'model_id': model_id,
                        'input_output': [
                            {
                                'input_field': 'summary',
                                'output_field': 'elser_embedding',
                            }
                        ]
                    }
                }
            ]
        )


class SearchEngine:
    def __init__(self, implementor):
        self.es = Elasticsearch('http://localhost:' + es_index_port, timeout=60)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.implementor = implementor(es=self.es)
        print('Connected to Elasticsearch!')
        print(self.es.info())

    def count_docs(self):
        return self.es.count(index=es_index_name)['count']

    def create_index(self):
        return self.implementor.create_index()

    def reindex(self):
        self.create_index()
        chunk_list = [key.decode('utf-8') for key in self.redis.lrange('chunk_list', 0, -1)]
        for chunk in chunk_list:
            members = self.redis.smembers(chunk)
            arguments = [json.loads(member.decode('utf-8')) for member in members]
            self.insert_documents(arguments)
            print(f'{chunk} ({len(arguments)} arguments)')

    def generate_summary_dataset(self):
        chunk_list = [key.decode('utf-8') for key in self.redis.lrange('chunk_list', 0, -1)]
        summaries = []  # List to hold all summaries

        for chunk in chunk_list:
            members = self.redis.smembers(chunk)
            arguments = [json.loads(member.decode('utf-8')) for member in members]

            for argument in arguments:
                processed = self.schema(argument)
                summaries.append({
                    'id': processed.get('id'),
                    'summary': processed.get('summary')
                })

        file_path = os.path.join(os.getcwd(), 'datasets', 'summary_dataset.json')

        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted existing file: {file_path}")

        with open(file_path, 'w') as f:
            json.dump(summaries, f, indent=2)
            print(f"Saved embeddings dataset to: {file_path}")

    def delete_index(self):
        if self.es.indices.exists(index=es_index_name):
            response = self.es.indices.delete(index=es_index_name)
            print("Index deleted:", response)
        else:
            print("Index does not exist.")

    def deploy_elser(self):
        if not search_mode == 'semantic':
            return
        return self.implementor.deploy()

    def retrieve_document(self, id):
        return self.es.get(index=es_index_name, id=id)

    def insert_documents(self, documents):
        operations = []

        for document in documents:
            schema = self.schema(document)

            if search_mode == 'hybrid':
                schema['embedding'] = self.implementor.get_embedding(schema['id'])

            operations.append({'index': {'_index': es_index_name}})
            operations.append(schema)

        response = self.es.bulk(operations=operations)
        errors = [item for item in response.get('items', []) if 'error' in item.get('index', {})]

        if errors:
            print("Some documents didn't index successfully")
        else:
            print("Chunk documents indexed successfully")

    def schema(self, document):
        core_info = document['metadata']['core']
        summary = self.generate_parsed_summary(document)

        return {
            "id": core_info['id'],
            "created": core_info['created'],
            "edited": core_info['edited'],
            "analyst_name": core_info.get('analyst_name', ''),
            "analyst_email": core_info.get('analyst_email', ''),
            "version": core_info['version'],
            "title": core_info['title'],
            "nodes": document['nodes'],
            "edges": document['edges'],
            "summary": summary
        }

    def generate_parsed_summary(self, document):
        combined_nodes = ', '.join(node['text'] for node in document.get('nodes', []))
        tokens = combined_nodes.split(' ')

        # Regular expression pattern for URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        filtered_tokens = []
        for token in tokens:

            if re.search(url_pattern, token):  # Remove URLs
                continue
            if token in punctuation_list:  # Remove punctuation
                continue
            if token.lower() in stopwords_list:  # Remove stopwords
                continue

            filtered_tokens.append(token)

        summary = ' '.join(filtered_tokens)
        return summary

    def search(self, raw_query, **query_args):
        parsed_query = self.implementor.parse_query(raw_query)
        return self.implementor.search(**parsed_query, **query_args)
