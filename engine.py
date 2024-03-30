from language.english.stopwords import stopwords_list
from language.english.punctuation import punctuation_list
from index import SearchIndex
from parser import SearchParser
from collections import Counter
# from pyinstrument import Profiler


class SearchEngine:
    def __init__(self):
        self.search_parser = SearchParser(punctuation_list, stopwords_list)
        self.index = SearchIndex()

    def add_document(self, doc_id, document):
        """Add a document to the index using simple concordance based on parsed text."""
        parsed_text = self.search_parser.parse(document)
        concordance = Counter(parsed_text)
        self.index.add_to_index(doc_id, concordance)

    def search(self, query):
        """Search the index for a query using simple concordance."""
        parsed_query = self.search_parser.parse(query)
        query_concordance = Counter(parsed_query)
        return self.index.get_matches(query_concordance)


# def profile_search_engine():
#     profiler = Profiler()
#     profiler.start()
#
#     main()
#
#     profiler.stop()
#     print(profiler.output_text(unicode=True, color=True))


def main():
    engine = SearchEngine()

    documents = {
        0: '''Advancing Argument Mining with Deep Learning Techniques Deep learning has revolutionized many fields, but its application in argument mining is particularly notable By analyzing patterns in large datasets, researchers can now identify argumentative structures and components with unprecedented accuracy, paving the way for more nuanced and comprehensive understanding of texts''',
        1: '''The Impact of Computational Argumentation on Public Debate This document explores how computational tools and algorithms are being used to analyze and shape public debates From identifying logical fallacies to enhancing the clarity of presented arguments, computational argumentation holds the potential to elevate the quality of public discourse''',
        2: '''Building More Persuasive AI Through Argumentation Theory Leveraging insights from traditional argumentation theory, AI developers are creating systems that can not only understand but also generate persuasive arguments This document delves into the methodologies behind these advancements and their implications for future AI applications''',
        3: '''Challenges in Automating Argument Evaluation Despite advances in computational argumentation, evaluating the strength and validity of arguments remains a significant challenge This piece discusses the complexities involved in automating argument evaluation, including the subjective nature of persuasion and the difficulty of encoding common sense reasoning''',
        4: '''Argumentation Frameworks A Comparative Study This document compares various argumentation frameworks, such as Dung's Abstract Argumentation Framework and the Toulmin Model, in the context of computational applications It discusses their strengths, weaknesses, and suitability for different types of argument analysis tasks''',
        5: '''Ethical Considerations in Computational Argumentation With the growing ability to automate argument analysis and generation, ethical questions emerge This text examines the responsibilities of developers to ensure these technologies are not misused, addressing concerns such as manipulation, bias, and transparency''',
        6: '''Integrating Computational Argumentation into Education This document explores the potential for computational argumentation tools to transform educational practices by providing students with feedback on their argumentative writing and reasoning skills, thereby fostering critical thinking and analytical abilities''',
        7: '''The Role of Argumentation in Decision Support Systems Highlighting the importance of argumentation in supporting decision-making processes, this text discusses how computational models can help individuals and organizations weigh options, evaluate evidence, and make more informed choices''',
        8: '''Argumentation Mining from Legal Texts Specialized challenges arise when mining arguments from legal documents due to their complex structure and language This document outlines the approaches being developed to extract and analyze argumentation in legal texts, facilitating applications such as case analysis and precedent research''',
        9: '''Future Directions in Computational Argumentation Speculating on the future, this piece discusses upcoming trends in computational argumentation, including the potential for real-time argument analysis in live debates, advancements in cross-domain argument mining, and the integration of argumentation technologies in everyday devices'''
    }

    for id, text in documents.items():
        engine.add_document(id, text)

    """
    Example search queries:
    
    - 'Ethical considerations in AI argumentation' => "The 'AI' token pollutes searches"
    - 'Deep learning in argument mining'
    - 'AI and public debate'
    - 'argumentation frameworks comparison'
    - 'The future of argument mining'
    """

    query = input("Enter your search query: ")
    results = engine.search(query)
    print("Search Results:")
    for result in results:
        score, doc_id = round(result[0], 2), result[1]
        text = documents[doc_id][:100]
        print(f'doc_id: {doc_id}, score: {score}, text: {text}')


if __name__ == "__main__":
    # profile_search_engine()
    main()
