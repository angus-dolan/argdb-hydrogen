import json
from pprint import pprint
import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from hydrogen.config import Config

load_dotenv()
config = Config()
index_name = config.get('search_index', 'index_name')
index_port = config.get('search_index', 'port')



# Vector search
class Search:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.es = Elasticsearch('http://localhost:' + index_port)
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)

    def search(self, **query_args):
        return self.es.search(index=index_name, **query_args)

    def create_index(self):
        self.es.indices.delete(index=index_name, ignore_unavailable=True)
        self.es.indices.create(index=index_name)

    def reindex(self):
        self.create_index()
        with open('data.json', 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents)

    def retrieve_document(self, id):
        return self.es.get(index=index_name, id=id)

    def get_embedding(self, text):
        return self.model.encode(text)

    def insert_document(self, document):
        parsed = self.transform_sadface(document)
        return self.es.index(index=index_name, document={
            **parsed,
            'embedding': self.get_embedding(parsed['summary']),
        })

    def transform_sadface(self, document):
        core_info = document['metadata']['core']
        output = {
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
        # Combine all node text into a summary
        summary = ' '.join(node['text'] for node in document['nodes'])
        output['summary'] = summary
        return output

    def insert_documents(self, documents):
        operations = []
        for document in documents:
            operations.append({'index': {'_index': index_name}})
            operations.append({
                **document,
                'embedding': self.get_embedding(document['summary']),
            })
        return self.es.bulk(operations=operations)

    def delete_index(self):
        if self.es.indices.exists(index=index_name):
            response = self.es.indices.delete(index=index_name)
            print("Index deleted:", response)
        else:
            print("Index does not exist.")

# Full text search
# class Search:
#     def __init__(self):
#         self.es = Elasticsearch('http://localhost:9200')
#         client_info = self.es.info()
#         print('Connected to Elasticsearch!')
#         pprint(client_info.body)
#
#     def search(self, **query_args):
#         return self.es.search(index=index_name, **query_args)
#
#     def create_index(self):
#         self.es.indices.delete(index=index_name, ignore_unavailable=True)
#         self.es.indices.create(index=index_name)
#
#     def reindex(self):
#         self.create_index()
#         with open('data.json', 'rt') as f:
#             documents = json.loads(f.read())
#         return self.insert_documents(documents)
#
#     def insert_document(self, document):
#         return self.es.index(index=index_name, body=document)
#
#     def insert_documents(self, documents):
#         operations = []
#         for document in documents:
#             operations.append({'index': {'_index': index_name}})
#             operations.append(document)
#         return self.es.bulk(operations=operations)
#
#     def retrieve_document(self, id):
#         return self.es.get(index=index_name, id=id)