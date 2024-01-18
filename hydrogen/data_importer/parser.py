from .models.argsme_token import ArgsmeToken
from .models.token import Token
from .sadface_builder import SadfaceBuilder
from .lexer import Lexer
from abc import ABC, abstractmethod
import sys

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
    
  def match(self, parser: Parser):
    type = parser.cur_token.type

    if type.name not in ArgsmeToken.__members__:
      parser.abort(f"Token type '{type}' is not a valid ArgsmeToken")

    if parser.cur_token.type != type:
      parser.abort(f"Expected {type.name}, got {parser.cur_token.type.name}")

    self.handle_token(parser.cur_token.type, parser.cur_token.value)
    parser.next_token()

  def handle_token(self, token_type, token_value):
    # Core metadata
    if token_type == ArgsmeToken.CTX_ACQ_TIME:
      self.builder.with_metadata_core("created", token_value)
      self.builder.with_metadata_core("edited", token_value)
    elif token_type == ArgsmeToken.ID:
      self.builder.with_metadata_core("id", token_value)
    # Other metadata
    if token_type == ArgsmeToken.CTX_SRC_TITLE:
      self.builder.with_metadata_other("argsme", "title", token_value)
    elif token_type == ArgsmeToken.PREMISES_TEXT:
      self.builder.with_metadata_other("argsme", "premise", token_value)
    elif token_type == ArgsmeToken.PREMISES_STANCE:
      self.builder.with_metadata_other("argsme", "premise_stance", token_value)
    elif token_type == ArgsmeToken.CONCLUSION:
      self.builder.with_metadata_other("argsme", "conclusion", token_value)
    # Node 
    # Edge

  def parse(self, parser: Parser):
    self.builder.default_metadata_core()

    while not parser.check_token(ArgsmeToken.EOF):
      self.match(parser)
    
    sadface_document = (
      self.builder
      .build()
    )

    print(self.builder.validate())
    print(sadface_document)
    
    # Call emitter
    # ...
