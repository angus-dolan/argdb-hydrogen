from hydrogen.search.parser import SearchParser
from hydrogen.search.index import SearchIndex
from collections import Counter
from pyinstrument import Profiler

class SearchEngine:
    def __init__(self):
        self.search_parser = SearchParser()
        self.index = SearchIndex()

    def generate_concordance(self, parsed_text):
        concordance = Counter()
        for token in parsed_text:
            edge_ngrams = self.index.generate_edge_ngrams(token)
            concordance.update(edge_ngrams)
        return concordance

    def add_document(self, doc_id, sadface_doc):
        nodes = sadface_doc.get('nodes')

        for node in nodes:
            parsed_text = self.search_parser.parse(node.get('text'))
            concordance = self.generate_concordance(parsed_text)
            self.index.add_to_index(doc_id, concordance)

    def search(self, query):
        parsed_query = self.search_parser.parse(query)
        query_concordance = self.generate_concordance(parsed_query)

        return self.index.get_matches(query_concordance)


def main():
    engine = SearchEngine()
    # query = input("Enter Search Term: ")
    query = "Something about high schools"
    results = engine.search(query)

    for relation, doc in results:
        print(f"Relevance: {relation}, Document: {doc[:200]}...")

    print("Number of results:" + str(len(results)))

def profile_search_engine():
    profiler = Profiler()
    profiler.start()

    main()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))

if __name__ == "__main__":
    profile_search_engine()