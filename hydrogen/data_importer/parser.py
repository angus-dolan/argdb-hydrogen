from .models.argsme_token import ArgsmeToken
from .models.token import Token
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

class ArgsmeParser(ParserStrategy):
  def __init__ (self):
    self.builder = SadfaceBuilder()
    self.id = ""
    self.previous_id = ""
    self.created = ""
    self.edited = ""
    self.title = ""
    self.conclusion = ""
    
  def match(self, parser: Parser):
    type = parser.cur_token.type

    if type.name not in ArgsmeToken.__members__:
      parser.abort(f"Token type '{type}' is not a valid ArgsmeToken")

    if parser.cur_token.type != type:
      parser.abort(f"Expected {type.name}, got {parser.cur_token.type.name}")

    # print(f"Matched {parser.cur_token.type.name} with value {parser.cur_token.value}")
    self.handle_token(parser.cur_token.type, parser.cur_token.value)
    parser.next_token()

  def handle_token(self, token_type, token_value):
    if token_type == ArgsmeToken.CTX_ACQ_TIME:
      self.created = token_value
      self.edited = token_value
    elif token_type == ArgsmeToken.ID:
      self.id = self.convert_to_uuid(token_value)
    elif token_type == ArgsmeToken.CTX_PREV_ID:
      self.previous_id = self.convert_to_uuid(token_value)
    if token_type == ArgsmeToken.CTX_SRC_TITLE:
      self.title = token_value
    elif token_type == ArgsmeToken.CONCLUSION:
      self.conclusion = token_value

  def convert_to_uuid(self, s):
    hashed = hashlib.sha1(s.encode()).hexdigest()
    shortened = hashed[:32]
    return str(uuid.UUID(shortened))
  
  def build_new_document(self):
    pass

  def parse(self, parser: Parser):
    self.builder.default_metadata_core()

    while not parser.check_token(ArgsmeToken.EOF):
      self.match(parser)
      
    if self.previous_id is "":
      # TODO: Call self.build_new_document()
      pass
    else:
      # TODO: Retrieve existing document
      # TODO: Add edge
      pass
      
    # We should still always have to add a node
    # regardless of if we're creating or updating
    self.builder.with_node({
      "id": self.id,
      "text": "",
      "type": "atom",
      "metadata": {}
    })
    
    sadface_document = (
      self.builder
      .build()
    )

    print(self.builder.validate())
    print(sadface_document)

    # Call emitter
    # ...
