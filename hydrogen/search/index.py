from hydrogen.config import Config
import math
import redis
import json

config = Config()
index_port = config.get('search_index', 'port')
index_name = config.get('search_index', 'index_name')

class SearchIndex:
    def __init__(self):
        self.client = redis.Redis(host='localhost', port=index_port, db=0, decode_responses=True)

    def add_to_index(self, doc_id, concordance):
        concordance = json.dumps(dict(concordance))
        self.client.sadd(f"{index_name}:{doc_id}", concordance)

    def get_matches(self, query_concordance):
        # TODO: This won't scale well, could need caching and DSA for checking what documents are worth searching
        document_keys = self.client.keys(f"{index_name}:*")
        matches = []

        for key in document_keys:
            concordance_json = self.client.smembers(key)

            for concordance_str in concordance_json:
                concordance = json.loads(concordance_str)
                relation = self.relation(query_concordance, concordance)
                if relation > 0:
                    # Extract doc_id from key
                    doc_id = key.split(':')[1]
                    matches.append((relation, doc_id))

        # Sort matches by relevance in descending order
        matches.sort(reverse=True, key=lambda x: x[0])
        return matches

    def magnitude(self, concordance):
        if not isinstance(concordance, dict):
            raise ValueError('Supplied argument should be of type dict')

        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    # TODO: Refactor this, call concordance1 'query_concordance'
    # TODO: Make it work with ngrams as keys rather than documents
    def relation(self, concordance1, concordance2):
        if not isinstance(concordance1, dict) or not isinstance(concordance2, dict):
            raise ValueError('Supplied arguments should be of type dict')

        relevance = 0
        for word, count in concordance1.items():
            if word in concordance2:
                relevance += count * concordance2[word]

        top_value = self.magnitude(concordance1) * self.magnitude(concordance2)
        if top_value != 0:
            return relevance / top_value
        else:
            return 0

    def generate_edge_ngrams(self, token, min_length=1, max_length=None):
        ngrams = []
        max_length = max_length or len(token)
        for n in range(min_length, min(max_length + 1, len(token) + 1)):
            ngrams.append(token[:n])
        return ngrams
