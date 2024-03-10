from hydrogen.search.language import punctuation_list, stopwords_list
import re


class SearchParser:
    def __init__(self):
        self.stopwords = stopwords_list
        self.punctuation = punctuation_list

    def remove_links(self, tokens):
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return [token for token in tokens if not re.search(url_pattern, token)]

    def remove_stopwords(self, tokens):
        return [word for word in tokens if word not in self.stopwords]

    def remove_punctuation(self, tokens):
        return [word for word in tokens if word not in self.punctuation]

    def parse(self, text):
        text = text.lower()

        # Add spaces around punctuation for token matching
        punctuation_pattern = f"([{re.escape(''.join(self.punctuation))}])"
        spaced_text = re.sub(punctuation_pattern, r" \1 ", text)
        text = re.sub(r"\s{2,}", " ", spaced_text)

        tokens = text.split(' ')
        tokens = self.remove_links(tokens)
        tokens = self.remove_stopwords(tokens)
        tokens = self.remove_punctuation(tokens)

        return tokens
