import math


class SearchIndex:
    def magnitude(self, concordance):
        if not isinstance(concordance, dict):
            raise ValueError('Supplied argument should be of type dict')

        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

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

    def concordance(self, document):
        if not isinstance(document, str):
            raise ValueError('Supplied argument should be of type string')

        con = {}
        for word in document.split(' '):
            if word in con:
                con[word] += 1
            else:
                con[word] = 1
        return con

    def generate_edge_ngrams(self, token, min_length=1, max_length=None):
        ngrams = []
        max_length = max_length or len(token)
        for n in range(min_length, min(max_length + 1, len(token) + 1)):
            ngrams.append(token[:n])
        return ngrams
