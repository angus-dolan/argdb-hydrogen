from hydrogen.search.parser import SearchParser
from hydrogen.search.index import SearchIndex
from collections import Counter
from pyinstrument import Profiler
from nltk.util import ngrams


class SearchEngine:
    def __init__(self):
        self.search_parser = SearchParser()
        self.index = SearchIndex()

    # def generate_concordance(self, parsed_text):
    #     concordance = Counter()
    #     for token in parsed_text:
    #         edge_ngrams = self.index.generate_edge_ngrams(token)
    #         concordance.update(edge_ngrams)
    #     return concordance

    def generate_edge_ngrams(self, text, max_length=3):
        edge_ngrams = []
        for word in text.split():
            for end in range(1, min(len(word), max_length) + 1):
                edge_ngrams.append(word[:end])
        return edge_ngrams

    def add_document(self, doc_id, sadface_doc):
        nodes = sadface_doc.get('nodes')

        for node in nodes:
            parsed_text = self.search_parser.parse(node.get('text'))
            edge_ngrams = self.generate_edge_ngrams(' '.join(parsed_text))
            n = self.generate_edge_ngrams("mens mental health")
            print()

    def search(self, query):
        parsed_query = self.search_parser.parse(query)
        query_concordance = self.generate_concordance(parsed_query)

        return self.index.get_matches(query_concordance)


def main():
    var = {
        "nodes": [
            {"id": "665a55a3-2019-04-19T12:46:15Z-00004-000", "metadata": {"stance": "PRO"},
             "text": "Physically fit people have better mental health and do better at academia", "type": "atom"},
        ]
    }

    engine = SearchEngine()
    engine.add_document("665a55a3-2019-04-19T12:46:15Z", var)


def profile_search_engine():
    profiler = Profiler()
    profiler.start()

    main()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))


if __name__ == "__main__":
    profile_search_engine()
