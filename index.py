import math


class SearchIndex:
    """
    This class uses in-memory storage to hold document concordances, supporting
    efficient text search through vector space modeling. It's simplified for
    demonstration purposes and quicker prototyping.
    """

    def __init__(self, index_name='search_index'):
        """
        Initializes the in-memory storage and sets the base name for the index.

        :param index_name: Base name for the index keys, used for demonstration.
        """
        self.documents = {}  # Stores document concordances
        self.index_name = index_name

    def add_to_index(self, doc_id, concordance):
        """
        Adds a document's concordance to the index in memory.

        :param doc_id: The document's identifier.
        :param concordance: A Counter object representing the document's concordance.
        """
        self.documents[doc_id] = concordance

    def get_matches(self, query_concordance):
        """
        Retrieves documents from the in-memory index that match the query concordance.

        :param query_concordance: A Counter object representing the query's concordance.
        :return: A list of tuples, each containing the match's relevance score and document ID.
        """
        matches = []
        for doc_id, concordance in self.documents.items():
            relation = self._relation(query_concordance, concordance)
            if relation > 0:
                matches.append((relation, doc_id))
        matches.sort(reverse=True, key=lambda x: x[0])
        return matches

    def _magnitude(self, concordance):
        """Calculates the magnitude of a concordance vector."""
        total = sum(count ** 2 for count in concordance.values())
        return math.sqrt(total)

    def _relation(self, concordance1, concordance2):
        """Calculates the relevance score between two concordances."""
        relevance = sum(concordance1.get(word, 0) * concordance2.get(word, 0) for word in concordance1)
        top_value = self._magnitude(concordance1) * self._magnitude(concordance2)
        return relevance / top_value if top_value != 0 else 0
