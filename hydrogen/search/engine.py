from parser import SearchParser
from index import SearchIndex


class SearchEngine:
    def __init__(self):
        self.search_parser = SearchParser()
        self.index = SearchIndex()
        self.documents = {}
        self.inverted_index = {}

    def add_document(self, doc_id, text):
        self.documents[doc_id] = text

        parsed_text = self.search_parser.parse(text)
        concordance = {}
        for token in parsed_text:
            edge_ngrams = self.index.generate_edge_ngrams(token)
            for ngram in edge_ngrams:
                if ngram in concordance:
                    concordance[ngram] += 1
                else:
                    concordance[ngram] = 1
        self.inverted_index[doc_id] = concordance

    def search(self, query):
        parsed_query = self.search_parser.parse(query)
        query_concordance = {}
        for token in parsed_query:
            edge_ngrams = self.index.generate_edge_ngrams(token)
            for ngram in edge_ngrams:
                query_concordance[ngram] = query_concordance.get(ngram, 0) + 1
        matches = []

        # TODO: This won't scale well, will need caching and DSA for checking what documents are worth searching
        for doc_id, concordance in self.inverted_index.items():
            relation = self.index.relation(query_concordance, concordance)
            if relation > 0:
                matches.append((relation, self.documents[doc_id]))
        matches.sort(reverse=True)

        return matches


if __name__ == "__main__":
    engine = SearchEngine()

    documents = {
        0: '''At Scale You Will Hit Every Performance Issue I used to think I knew a bit about performance scalability and how to keep things trucking when you hit large amounts of data Truth is I know diddly squat on the subject since the most I have ever done is read about how its done To understand how I came about realising this you need some background''',
        1: '''Richard Stallman to visit Australia Im not usually one to promote events and the like unless I feel there is a genuine benefit to be had by attending but this is one stands out Richard M Stallman the guru of Free Software is coming Down Under to hold a talk You can read about him here Open Source Celebrity to visit Australia''',
        2: '''MySQL Backups Done Easily One thing that comes up a lot on sites like Stackoverflow and the like is how to backup MySQL databases The first answer is usually use mysqldump This is all fine and good till you start to want to dump multiple databases You can do this all in one like using the all databases option however this makes restoring a single database an issue since you have to parse out the parts you want which can be a pain''',
        3: '''Why You Shouldnt roll your own CAPTCHA At a TechEd I attended a few years ago I was watching a presentation about Security presented by Rocky Heckman read his blog its quite good In it he was talking about security algorithms The part that really stuck with me went like this''',
        4: '''The Great Benefit of Test Driven Development Nobody Talks About The feeling of productivity because you are writing lots of code Think about that for a moment Ask any developer who wants to develop why they became a developer One of the first things that comes up is I enjoy writing code This is one of the things that I personally enjoy doing Writing code any code especially when its solving my current problem makes me feel productive It makes me feel like Im getting somewhere Its empowering''',
        5: '''Setting up GIT to use a Subversion SVN style workflow Moving from Subversion SVN to GIT can be a little confusing at first I think the biggest thing I noticed was that GIT doesnt have a specific workflow you have to pick your own Personally I wanted to stick to my Subversion like work-flow with a central server which all my machines would pull and push too Since it took a while to set up I thought I would throw up a blog post on how to do it''',
        6: '''Why CAPTCHA Never Use Numbers 0 1 5 7 Interestingly this sort of question pops up a lot in my referring search term stats Why CAPTCHAs never use the numbers 0 1 5 7 Its a relativity simple question with a reasonably simple answer Its because each of the above numbers are easy to confuse with a letter See the below''',
    }

    for doc_id, text in documents.items():
        engine.add_document(doc_id, text)

    query = input("Enter Search Term: ")
    results = engine.search(query)

    for relation, doc in results:
        print(f"Relevance: {relation}, Document: {doc[:100]}...")
