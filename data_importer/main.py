from .lexer import *
from .parser import *
from .emitter import *

file_path = 'example_data/argsme-example.json'

def load_json_as_string(file_path):
  with open(file_path, 'r') as file:
    data_string = file.read()
    return data_string

class DataImporter:
  def __init__(self, input_data=None):
    self.input = load_json_as_string(file_path)

  def import_file(self):
    source = '{ "premises": [{"text": "Hello World! this is my premise...","stance": "CON"}],"context": {"sourceId": "70a50579-2019-04-18T19:55:39Z","previousArgumentInSourceId": "70a50579-2019-04-18T19:55:39Z-00003-000","acquisitionTime": "2019-04-18T19:55:39Z","discussionTitle": "Is music piracy a bad thing?","sourceTitle": "Debate Argument: Music Piracy in the USA | Debate.org","sourceUrl": "https://www.debate.org/debates/","nextArgumentInSourceId": "70a50579-2019-04-18T19:55:39Z-00005-000"}, "id": "70a50579-2019-04-18T19:55:39Z-00004-000", "conclusion": "Music piracy is a bad thing."}'
    # source = "+- # This is a comment!\n */"
    lexer = Lexer(source, ArgsmeLexer())
    lexer.tokenize_source()
