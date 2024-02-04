from models.tokens import Token, ArgsmeToken
from .sadface_builder import SadfaceBuilder
from .lexer import Lexer
from database import Database
from abc import ABC, abstractmethod
import sys
import uuid
import hashlib
import json 
import logging

db = Database()

class ParserStrategy(ABC):
  @abstractmethod
  def parse(self):
    pass

class Parser:
  def __init__(self, parser_strategy: ParserStrategy, lexer: Lexer):
    self._parser_strategy = parser_strategy
    self.lexer = lexer
    self.cur_token = None
    self.peek_token = None
    self.uuid = None
    self.document = None
    self.next_token()
    self.next_token() # Call this twice to initialize current and peek

  def set_parser_strategy(self, parser_strategy: ParserStrategy):
    self._parser_strategy = parser_strategy

  def parse_tokens(self):
    return self._parser_strategy.parse(self)
  
  def check_token(self, type):
    return type == self.cur_token.type

  def check_peek(self, type):
    return type == self.peek_token.type

  def next_token(self):
    self.cur_token = self.peek_token
    self.peek_token = Token('', ArgsmeToken.EOF)

    if self.lexer.tokens:
      self.peek_token = self.lexer.tokens.popleft()

  def abort(self, message):
    sys.exit("Error: " + message) # TODO: Add logging

class DataHandler(ABC):
  def convert_to_uuid(self, string):
    if string == "": return ""
    hashed = hashlib.sha1(string.encode()).hexdigest()
    shortened = hashed[:32]
    return str(uuid.UUID(shortened))

  @abstractmethod
  def handle_token(self, token_type, token_value):
    pass

class ArgsmeDataHandler(DataHandler):
  def __init__(self):
    self.id = ""
    self.source_id = ""
    self.previous_id = ""
    self.created = ""
    self.edited = ""
    self.title = ""
    self.conclusion = ""
    self.premise_txt = ""
    self.stance = ""

    self.token_handlers = {
      ArgsmeToken.CTX_ACQ_TIME: self.handle_acq_time,
      ArgsmeToken.CTX_SRC_ID: self.handle_src_id,
      ArgsmeToken.ID: self.handle_id,
      ArgsmeToken.CTX_PREV_ID: self.handle_prev_id,
      ArgsmeToken.CTX_TITLE: self.handle_title,
      ArgsmeToken.CONCLUSION: self.handle_conclusion,
      ArgsmeToken.PREMISES_TEXT: self.handle_premise_txt,
      ArgsmeToken.PREMISES_STANCE: self.handle_stance,
    }

  def handle_acq_time(self, value):
    self.created = value
    self.edited = value

  def handle_src_id(self, value):
    self.source_id = self.convert_to_uuid(value)

  def handle_id(self, value):
    self.id = self.convert_to_uuid(value)

  def handle_prev_id(self, value):
    self.previous_id = self.convert_to_uuid(value)
  
  def handle_title(self, value):
    self.title = value
  
  def handle_conclusion(self, value):
    self.conclusion = value
  
  def handle_premise_txt(self, value):
    self.premise_txt = value
  
  def handle_stance(self, value):
    self.stance = value

  def handle_token(self, parser: Parser):
    argsme_type = parser.cur_token.type
    handler = self.token_handlers.get(argsme_type)

    if handler:
      token_value = parser.cur_token.value
      handler(token_value)
    
class ArgsmeParser(ParserStrategy):
  def __init__ (self):
    self.builder = SadfaceBuilder()
    self.data_handler = ArgsmeDataHandler()
    
  def match(self, parser: Parser):    
    self.data_handler.handle_token(parser)
    parser.next_token()
  
  def get_node(self):
    return {
      "id": self.data_handler.id,
      "metadata": {
        "stance": self.data_handler.stance,
      },
      "text": self.data_handler.premise_txt,
      "type": "atom",
    }
  
  def get_edge(self):
    return {
      "source_id": self.data_handler.previous_id,
      "target_id": self.data_handler.id
    }

  def build_new_document(self):
    self.builder.with_metadata_core("id", self.data_handler.source_id)
    self.builder.with_metadata_core("created", self.data_handler.created)
    self.builder.with_metadata_core("edited", self.data_handler.edited)
    self.builder.with_metadata_core("title", self.data_handler.title)
    self.builder.with_node(self.get_node())

  def update_existing_document(self, parser: Parser):
    result = db.raw.get(self.data_handler.source_id)
    
    if result is None: 
      parser.abort(f"Document with source_id {self.data_handler.source_id} does not exist")

    document = json.loads(result.data)
    self.builder.with_existing_document(document)
    self.builder.with_node(self.get_node())
    self.builder.with_edge(self.get_edge())

  def parse(self, parser: Parser):
    parser.document = None
    parser.uuid = None
    
    while not parser.check_token(ArgsmeToken.EOF):
      self.match(parser)
    
    if self.data_handler.previous_id == "":
      self.build_new_document()
    else:
      self.update_existing_document(parser)
    
    parsed_document = (self.builder.build())
    valid, error_messages = self.builder.validate()

    # if valid:
    parser.document = parsed_document
    parser.uuid = self.data_handler.source_id
    # else:
    #   parser.abort(f"Document is not valid. Errors: {error_messages}")
