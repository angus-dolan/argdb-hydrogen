from .lexer import *
from .parser import *
from .emitter import *

class DataImporter:
  def import_file(self):
    source = '{ "premises": [{"text": "Hello World! this is my premise...","stance": "CON"}],"context": {"sourceId": "70a50579-2019-04-18T19:55:39Z","previousArgumentInSourceId": "70a50579-2019-04-18T19:55:39Z-00003-000","acquisitionTime": "2019-04-18T19:55:39Z","discussionTitle": "Is music piracy a bad thing?","sourceTitle": "Debate Argument: Music Piracy in the USA | Debate.org","sourceUrl": "https://www.debate.org/debates/","nextArgumentInSourceId": "70a50579-2019-04-18T19:55:39Z-00005-000"}, "id": "70a50579-2019-04-18T19:55:39Z-00004-000", "conclusion": "Music piracy is a bad thing."}'
    
    argsme_lexer = ArgsmeLexer()
    lexer = Lexer(argsme_lexer, source)
    lexer.tokenize_source()

    argsme_parser = ArgsmeParser()
    parser = Parser(argsme_parser, lexer)
    parser.parse_tokens()




