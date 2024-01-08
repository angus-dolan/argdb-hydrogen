from .models.argsme_token import ArgsmeToken
from .models.token import Token
from abc import ABC, abstractmethod
import sys

class LexerStrategy(ABC):
  @abstractmethod
  def tokenize(self, lexer):
    pass

class Lexer:
  def __init__(self, source, lexer_strategy: LexerStrategy):
    self._lexer_strategy = lexer_strategy
    self.source = self.preprocess_source(source)
    self.cur_char = ''
    self.cur_pos = -1
    self.next_char()

  def preprocess_source(self, source):
    in_string = False
    processed_source = ''

    for char in source:
      if char == '"' and (len(processed_source) == 0 or processed_source[-1] != '\\'):
        in_string = not in_string
      if not in_string and char in [' ', '\t', '\r']:
        continue
      processed_source += char

    return processed_source + '\0'

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
  
  def skip_whitespace(self):
    while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
      self.next_char()
  
  def peek(self):
    if self.cur_pos + 1 >= len(self.source):
      return '\0'
    return self.source[self.cur_pos+1]
  
  def lookahead(self, length):
    end_pos = self.cur_pos + length
    if end_pos >= len(self.source):
        return self.source[self.cur_pos:]
    return self.source[self.cur_pos:end_pos]
  
  def abort(self, message):
    sys.exit("Lexing error: " + message) # Invalid token found

class ArgsmeLexer(LexerStrategy):
  def __init__(self):
    self.tokens = []

  def get_token(self, lexer):
    lexer.skip_whitespace()

    # JSON specific tokens
    if lexer.cur_char == '{':
      self.tokens.append(Token(lexer.cur_char, ArgsmeToken.CURLY_OPEN))
    elif lexer.cur_char == '}':
      self.tokens.append(Token(lexer.cur_char, ArgsmeToken.CURLY_CLOSE))
    elif lexer.cur_char == '[':
      self.tokens.append(Token(lexer.cur_char, ArgsmeToken.SQUARE_OPEN))
    elif lexer.cur_char == ']':
      self.tokens.append(Token(lexer.cur_char, ArgsmeToken.SQUARE_CLOSE))
    elif lexer.cur_char == ':':
      self.tokens.append(Token(lexer.cur_char, ArgsmeToken.COLON))
    elif lexer.cur_char == ',':
      self.tokens.append(Token(lexer.cur_char, ArgsmeToken.COMMA))
      
    elif lexer.cur_char == '"':
      self.process_argsme_keywords(lexer)

    # EOF and unknown tokens
    elif lexer.cur_char == '\0':
      self.tokens.append(Token('', ArgsmeToken.EOF))
    else:
      lexer.abort(f"Unknown token: {lexer.cur_char}")

    lexer.next_char()

  def process_argsme_keywords(self, lexer):
      string_content = self.argsme_lookahead(lexer)

      if string_content == "premises":
        self.tokens.append(Token(string_content, ArgsmeToken.PREMISES))
      elif string_content == "text":
        lexer.next_char()
        text_token = self.argsme_lookahead(lexer)
        self.tokens.append(Token(text_token, ArgsmeToken.PREMISES_TEXT))
      elif string_content == "stance":
        lexer.next_char()
        text_token = self.argsme_lookahead(lexer)
        self.tokens.append(Token(text_token, ArgsmeToken.PREMISES_STANCE))
      else:
        self.tokens.append(Token(string_content, ArgsmeToken.STRING))
  
  def argsme_lookahead(self, lexer):
    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      if lexer.cur_char == ':':
        self.tokens.append(Token(lexer.cur_char, ArgsmeToken.COLON))
      lexer.next_char()

    lexer.next_char() # Skip the opening quote
    string_content = ''

    # Collect characters until the closing quotation mark or end of file
    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      string_content += lexer.cur_char
      lexer.next_char()
      if lexer.cur_char == '\0':
        lexer.abort("String literal not terminated")

    return string_content.strip()
  
  def tokenize(self, lexer):
    print(lexer.source)
    self.get_token(lexer)
    while self.tokens[-1].kind != ArgsmeToken.EOF:
      token = self.tokens[-1]
      print(token.kind, ":", token.text)
      self.get_token(lexer)
    return self.tokens
