import re


class SearchParser:
    """
    This class is responsible for parsing text by lowering case, removing links,
    stopwords, and punctuation, and then splitting the text into tokens.
    """

    def __init__(self, stopwords_list, punctuation_list):
        """
        Initializes the SearchParser with a list of stopwords and punctuation.

        :param stopwords_list: A list of stopwords to be removed from the text.
        :param punctuation_list: A list of punctuation marks to be removed from the text.
        """
        self.stopwords = stopwords_list
        self.punctuation = punctuation_list

    def parse(self, text):
        """
        Parses the given text into tokens after cleaning it.

        :param text: The text to parse.
        :return: A list of tokens.
        """
        text = text.lower()
        tokens = text.split(' ')
        tokens = self._remove_links(tokens)
        tokens = self._remove_stopwords(tokens)
        tokens = self._remove_punctuation(tokens)
        return tokens

    def _remove_links(self, tokens):
        """Removes any tokens that are links."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return [token for token in tokens if not re.search(url_pattern, token)]

    def _remove_stopwords(self, tokens):
        """Removes stopwords from the list of tokens."""
        return [word for word in tokens if word not in self.stopwords]

    def _remove_punctuation(self, tokens):
        """Removes punctuation from the list of tokens."""
        return [word for word in tokens if word not in self.punctuation]
