from .lexer import *
from .parser import *
from .emitter import *
import pyjq
import json
import os

class DataImporter:
  def import_file(self):
    file_path = './data_importer/example_data/physical_vs_mental.json'

    if not os.path.exists(file_path):
      return print(f"File not found: {file_path}")

    with open(file_path, 'r') as file:
      data = json.load(file)

    num_args_ql = '.arguments | length'
    num_args = pyjq.first(num_args_ql, data)
    print(f"Number of arguments: {num_args}")

    for i in range(num_args):
      argument_query = f".arguments[{i}]"
      argument = pyjq.first(argument_query, data)

      source = json.dumps(argument)
      argsme_lexer = ArgsmeLexer()
      lexer = Lexer(argsme_lexer, source)
      lexer.tokenize_source()

      argsme_parser = ArgsmeParser()
      parser = Parser(argsme_parser, lexer)
      parser.parse_tokens()

      emitter = Emitter(parser.uuid, parser.document)
      emitter.emit()
