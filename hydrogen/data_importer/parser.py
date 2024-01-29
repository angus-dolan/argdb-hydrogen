from models.tokens import Token, ArgsmeToken
from database import Database, db, Document, Raw
from .sadface_builder import SadfaceBuilder
from .lexer import Lexer
from abc import ABC, abstractmethod
import sys
import uuid
import hashlib

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
    if self.lexer.tokens:
      self.peek_token = self.lexer.tokens.popleft()
    else:
      self.peek_token = Token('', ArgsmeToken.EOF)

  def abort(self, message):
    sys.exit("Error. " + message)

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
    self.previous_id = ""
    self.created = ""
    self.edited = ""
    self.title = ""
    self.conclusion = ""
    self.premise = ""
    self.stance = ""

    self.token_handlers = {
      ArgsmeToken.CTX_ACQ_TIME: self.handle_acq_time,
      ArgsmeToken.ID: self.handle_id,
      ArgsmeToken.CTX_PREV_ID: self.handle_prev_id,
      ArgsmeToken.CTX_TITLE: self.handle_title,
      ArgsmeToken.CONCLUSION: self.handle_conclusion,
      ArgsmeToken.PREMISES_TEXT: self.handle_premise,
      ArgsmeToken.PREMISES_STANCE: self.handle_stance,
    }

  def handle_acq_time(self, value):
    self.created = value
    self.edited = value

  def handle_id(self, value):
    self.id = self.convert_to_uuid(value)

  def handle_prev_id(self, value):
    self.previous_id = self.convert_to_uuid(value)
  
  def handle_title(self, value):
    self.title = value
  
  def handle_conclusion(self, value):
    self.conclusion = value
  
  def handle_premise(self, value):
    self.premise = value
  
  def handle_stance(self, value):
    self.stance = value

  def handle_token(self, parser: Parser):
    token_type = parser.cur_token.type
    token_value = parser.cur_token.value
    handler = self.token_handlers.get(token_type)

    if handler:
      handler(token_value)
    
class ArgsmeParser(ParserStrategy):
  def __init__ (self):
    self.builder = SadfaceBuilder()
    self.data_handler = ArgsmeDataHandler()
    
  def match(self, parser: Parser):
    type = parser.cur_token.type

    if type.name not in ArgsmeToken.__members__:
      parser.abort(f"Token type '{type}' is not a valid ArgsmeToken")

    if parser.cur_token.type != type:
      parser.abort(f"Expected {type.name}, got {parser.cur_token.type.name}")

    self.data_handler.handle_token(parser)
    parser.next_token()
  
  def add_node(self):
    return self.builder.with_node({
      "id": self.data_handler.id,
      "metadata": {
        "premise": self.data_handler.premise,
        "stance": self.data_handler.stance,
      },
      "text": self.data_handler.conclusion,
      "type": "atom",
    })
  
  def build_new_document(self):
    self.builder.with_metadata_core("id", self.data_handler.id)
    self.builder.with_metadata_core("created", self.data_handler.created)
    self.builder.with_metadata_core("edited", self.data_handler.edited)
    self.builder.with_metadata_core("title", self.data_handler.title)

    self.add_node()

  def update_existing_document(self):
    print("Updating existing document")
    # TODO: Retrieve existing document
    # TODO: Add node
    # TODO: Add edge
    pass

  def parse(self, parser: Parser):
    while not parser.check_token(ArgsmeToken.EOF):
      self.match(parser)
    
    if self.data_handler.previous_id == "":
      self.build_new_document()
    else:
      self.update_existing_document()
    
    sadface_document = (self.builder.build())
    validation_result, error_messages = self.builder.validate()

    print(sadface_document)

    # Call emitter
    # db.raw.insert_one(Raw(uuid=self.id, data=json.dumps(sadface_document)))
    # ...
