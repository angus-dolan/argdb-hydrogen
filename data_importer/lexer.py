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
  
  def abort(self, message):
    sys.exit("Lexing error: " + message) # Invalid token found

class ArgsmeLexer(LexerStrategy):
  def __init__(self):
    self.tokens = []
    self.token_map = {
      # JSON-specific tokens
      '{': ArgsmeToken.CURLY_OPEN,
      '}': ArgsmeToken.CURLY_CLOSE,
      '[': ArgsmeToken.SQUARE_OPEN,
      ']': ArgsmeToken.SQUARE_CLOSE,
      ':': ArgsmeToken.COLON,
      ',': ArgsmeToken.COMMA,
      # Argsme-specific tokens
      'premises': ArgsmeToken.PREMISES,
      'text': ArgsmeToken.PREMISES_TEXT,
      'stance': ArgsmeToken.PREMISES_STANCE,
      'context': ArgsmeToken.CTX,
      'sourceId': ArgsmeToken.CTX_ID,
      'previousArgumentInSourceId': ArgsmeToken.CTX_PREV_ID,
      'acquisitionTime': ArgsmeToken.CTX_ACQ_TIME,
      'discussionTitle': ArgsmeToken.CTX_TITLE,
      'sourceTitle': ArgsmeToken.CTX_URL,
      'sourceUrl': ArgsmeToken.CTX_NEXT_ID,
      'id': ArgsmeToken.ID,
      'conclusion': ArgsmeToken.CONCLUSION,
    }
    self.standalone_map = {
      'premises',
      'context'
    }
  def next_token(self, lexer):
    lexer.skip_whitespace()

    if lexer.cur_char in ['{', '}', '[', ']', ':', ',']:
      return self.handle_json(lexer)
    elif lexer.cur_char == '"':
      return self.handle_keyword(lexer)
    elif lexer.cur_char == '\0':
      return Token('', ArgsmeToken.EOF)
    else:
      lexer.abort(f"Unknown token: {lexer.cur_char}")

  def handle_json(self, lexer):
    token = Token(lexer.cur_char, self.get_json_type(lexer.cur_char))
    lexer.next_char()
    return token

  def handle_keyword(self, lexer):
    lexer.next_char()  # Skip the opening quote
    keyword = ''

    while lexer.cur_char != '"' and lexer.cur_char != '\0':
        keyword += lexer.cur_char
        lexer.next_char()
        if lexer.cur_char == '\0':
            lexer.abort("Keyword not terminated")

    lexer.next_char()  # Skip the closing quote of the value
    print(keyword)
    # if keyword in self.standalone_map:
    #     return Token(keyword, self.token_map[keyword])
    # elif keyword in self.token_map:
    #     value = self.get_keyword_value(lexer)
    #     print(value)
    #     return Token('', ArgsmeToken.STRING)
    #     # return Token(value, self.token_map[keyword])
    # else:
    
    return Token('', ArgsmeToken.STRING)
  
  def get_keyword_value(self, lexer):
    lexer.next_char()  # Skip the opening quote of the value
    value = ''

    while lexer.cur_char != '"' and lexer.cur_char != '\0':
        value += lexer.cur_char
        lexer.next_char()
        if lexer.cur_char == '\0':
            lexer.abort("Value not terminated")

    lexer.next_char()  # Skip the closing quote of the value
    return value
  
  def get_json_type(self, char):
     return {
        '{': ArgsmeToken.CURLY_OPEN,
        '}': ArgsmeToken.CURLY_CLOSE,
        '[': ArgsmeToken.SQUARE_OPEN,
        ']': ArgsmeToken.SQUARE_CLOSE,
        ':': ArgsmeToken.COLON,
        ',': ArgsmeToken.COMMA,
    }.get(char, ArgsmeToken.UNKNOWN)
  
  def keyword_lookahead(self, lexer):
    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      if lexer.cur_char == ':':
        self.tokens.append(Token(lexer.cur_char, ArgsmeToken.COLON))
      lexer.next_char()

    lexer.next_char() # Skip the opening quote
    string_content = ''

    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      string_content += lexer.cur_char
      lexer.next_char()
      if lexer.cur_char == '\0':
        lexer.abort("String literal not terminated")

    return string_content.strip()
  
  def tokenize(self, lexer):
    print(lexer.source)
    token = self.next_token(lexer)
    while token.kind != ArgsmeToken.EOF:
      print(token.kind, ":", token.text)
      token = self.next_token(lexer)
    return self.tokens