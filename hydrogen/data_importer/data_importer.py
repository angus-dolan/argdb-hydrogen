from .lexer import *
from .parser import *
from .emitter import *
from log_config import setup_logging
import pyjq
import json
import os
import time
import logging

logger = logging.getLogger(__name__)
class DataImporter:
  def __init__(self, file_path):
    setup_logging('data_importer.log')    
    self.file_path = file_path
    self.data = None
    self.num_args = 0
    self.load_file()
    self.get_num_args()

  def abort(self, message):
    logger.exception(message)
    sys.exit()

  def load_file(self):
    if not os.path.exists(self.file_path):
      self.abort(f"File does not exist: {self.file_path}")
      raise
    with open(self.file_path, 'r') as file:
      self.data = json.load(file)

  def get_num_args(self):
    self.num_args = pyjq.first('.arguments | length', self.data)

  def import_file(self):
    try: 
      start_time = time.time()
      for i in range(self.num_args):
        argument = pyjq.first(f".arguments[{i}]", self.data)

        lexer = Lexer(ArgsmeLexer(), json.dumps(argument))
        lexer.tokenize_source()

        parser = Parser(ArgsmeParser(), lexer)
        parser.parse_tokens()

        emitter = Emitter(parser.uuid, parser.document)
        emitter.emit()

      end_time = time.time()
      elapsed_time = end_time - start_time
      print(f"Elapsed time: {elapsed_time} seconds")
    except Exception as e:
      logger.exception("Failed to import file: %s", e)
      raise
