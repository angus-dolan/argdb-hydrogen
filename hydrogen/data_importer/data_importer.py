from .lexer import *
from .parser import *
from .emitter import *

class DataImporter:
  def import_file(self):
    source_0 = '{"premises": [{"text": "Argument 00000","stance": "CON"},],"context": {"sourceId": "759e7c52-2019-04-18T14:37:21Z","previousArgumentInSourceId": "","acquisitionTime": "2019-04-18T14:37:21Z","discussionTitle": "Individual human rights and liberties should transcend or out-rank the rights given to corporations.","sourceTitle": "Online Debate: Individual human rights and liberties should transcend or out-rank the rights given to corporations. | Debate.org","sourceUrl": "https://www.debate.org/debates/Individual-human-rights-and-liberties-should-transcend-or-out-rank-the-rights-given-to-corporations./1/","nextArgumentInSourceId": "759e7c52-2019-04-18T14:37:21Z-00001-000"},"id": "759e7c52-2019-04-18T14:37:21Z-00000-000","conclusion": "Individual human rights and liberties should transcend or out-rank the rights given to corporations."},'
    source_1 = '{"premises": [{"text": "Argument 00001","stance": "PRO"}],"context": {"sourceId": "759e7c52-2019-04-18T14:37:21Z","previousArgumentInSourceId": "759e7c52-2019-04-18T14:37:21Z-00000-000","acquisitionTime": "2019-04-18T14:37:21Z","discussionTitle": "Individual human rights and liberties should transcend or out-rank the rights given to corporations.","sourceTitle": "Online Debate: Individual human rights and liberties should transcend or out-rank the rights given to corporations. | Debate.org","sourceUrl": "https://www.debate.org/debates/Individual-human-rights-and-liberties-should-transcend-or-out-rank-the-rights-given-to-corporations./1/","nextArgumentInSourceId": "759e7c52-2019-04-18T14:37:21Z-00002-000"},"id": "759e7c52-2019-04-18T14:37:21Z-00001-000","conclusion": "Individual human rights and liberties should transcend or out-rank the rights given to corporations."},'

    argsme_lexer = ArgsmeLexer()
    lexer = Lexer(argsme_lexer, source_1)
    lexer.tokenize_source()

    argsme_parser = ArgsmeParser()
    parser = Parser(argsme_parser, lexer)
    parser.parse_tokens()
