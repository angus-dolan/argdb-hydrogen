from .models.argsme_token import ArgsmeToken
from .models.token import Token
from collections import deque
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
  
  # Return true if the current token matches
  def check_token(self, type):
    return type == self.cur_token.type

  # Return true if the next token matches
  def check_peek(self, type):
    return type == self.peek_token.type

  # Try to match current token. If not, error. Advances the current token
  def match(self, type):
    if not self.check_token(type):
      self.abort("Expected " + type.name + ", got " + self.cur_token.type.name)
    self.next_token()
  
  # Advances the current token
  def next_token(self):
    self.cur_token = self.peek_token
    if self.lexer.tokens:
      self.peek_token = self.lexer.tokens.popleft()
    else:
      self.peek_token = Token('', ArgsmeToken.EOF)

  def abort(self, message):
    sys.exit("Error. " + message)

class ArgsmeParser(ParserStrategy):
  def parse(self, parser):
    print("Parsing...")
    while not parser.check_token(ArgsmeToken.EOF):
      print(f"Token: {parser.cur_token.type.name}, Value: {parser.cur_token.value}")
      parser.next_token()
