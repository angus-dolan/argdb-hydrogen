from .models.token import Token
from .models.argsme_token import ArgsmeToken
from abc import ABC, abstractmethod
import sys

class LexerStrategy(ABC):
  @abstractmethod
  def tokenize(self, lexer):
    pass

class Lexer:
  def __init__(self, source, lexer_strategy: LexerStrategy):
    self._lexer_strategy = lexer_strategy
    self.source = source + '\n' 
    self.cur_char = ''
    self.cur_pos = -1
    self.next_char()

  def set_lexer_strategy(self, lexer_strategy: LexerStrategy):
    self._lexer_strategy = lexer_strategy

  def tokenize_source(self):
    return self._lexer_strategy.tokenize(self)

  def next_char(self):
    self.cur_pos += 1
    if self.cur_pos >= len(self.source):
      self.cur_char = '\0' # EOF
    else:
      self.cur_char = self.source[self.cur_pos]

  def peek(self):
    if self.cur_pos + 1 >= len(self.source):
      return '\0'
    return self.source[self.cur_pos+1]

  def abort(self, message):
    sys.exit("Lexing error: " + message) # Invalid token found
  
  def skip_whitespace(self):
    while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
      self.next_char()
  
  def skip_comment(self):
    if self.cur_char == '#':
      while self.cur_char != '\n':
        self.next_char()

  def process_string_literal(self, lexer):
    lexer.next_char() # Skip the opening quote
    start_pos = lexer.cur_pos

    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      lexer.next_char()
    if lexer.cur_char == '\0':
      lexer.abort("String literal not terminated")

    string_content = lexer.source[start_pos:lexer.cur_pos]
    lexer.next_char() # Skip the closing quote
    return string_content.strip()
  
class ArgsmeLexer(LexerStrategy):
  def get_token(self, lexer):
    lexer.skip_whitespace()
    lexer.skip_comment()

    token = None

    # JSON specific tokens
    if lexer.cur_char == '{':
      token = Token(lexer.cur_char, ArgsmeToken.CURLY_OPEN)
    elif lexer.cur_char == '}':
      token = Token(lexer.cur_char, ArgsmeToken.CURLY_CLOSE)
    elif lexer.cur_char == '[':
      token = Token(lexer.cur_char, ArgsmeToken.SQUARE_OPEN)
    elif lexer.cur_char == ']':
      token = Token(lexer.cur_char, ArgsmeToken.SQUARE_CLOSE)
    elif lexer.cur_char == ':':
      token = Token(lexer.cur_char, ArgsmeToken.COLON)
    elif lexer.cur_char == ',':
      token = Token(lexer.cur_char, ArgsmeToken.COMMA)
      
    # String literals
    elif lexer.cur_char == '"':
      token = self.process_argsme_keywords(lexer)
    elif lexer.cur_char == '\0':
      token = Token('', ArgsmeToken.EOF)
    else:
      lexer.abort(f"Unknown token: {lexer.cur_char}")

    lexer.next_char()
    return token
  
  def process_argsme_keywords(self, lexer):
    string_content = lexer.process_string_literal(lexer)
    if string_content == 'premises':
      return Token(string_content, ArgsmeToken.PREMISES)
    else:
      return Token(string_content, ArgsmeToken.STRING)
  
  def tokenize(self, lexer):
    token = self.get_token(lexer)
    while token.kind != ArgsmeToken.EOF:
      print(token.kind, ":", token.text)
      token = self.get_token(lexer)

