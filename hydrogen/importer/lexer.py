from models.tokens import Token, ArgsmeToken
from collections import deque
from abc import ABC, abstractmethod
import sys
import logging

logger = logging.getLogger(__name__)

class LexerStrategy(ABC):
  @abstractmethod
  def tokenize(self, lexer):
    pass

class Lexer:
  def __init__(self, lexer_strategy: LexerStrategy, source, id):
    self.id = id
    self.tokens = deque()
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
  
  def abort(self, message, argument_id=None):
    error_message = f'Lexing error: {message}'
    if argument_id:
      error_message += f' | Argument ID: {argument_id}'
    logger.error(error_message)
    sys.exit(error_message)

class ArgsmeLexer(LexerStrategy):
  def __init__(self):
    self.keywords_map = {
      'premises': ArgsmeToken.PREMISES,
      'text': ArgsmeToken.PREMISES_TEXT,
      'stance': ArgsmeToken.PREMISES_STANCE,
      'context': ArgsmeToken.CTX,
      'sourceId': ArgsmeToken.CTX_SRC_ID,
      'previousArgumentInSourceId': ArgsmeToken.CTX_PREV_ID,
      'acquisitionTime': ArgsmeToken.CTX_ACQ_TIME,
      'discussionTitle': ArgsmeToken.CTX_TITLE,
      'sourceTitle': ArgsmeToken.CTX_SRC_TITLE,
      'sourceUrl': ArgsmeToken.CTX_SRC_URL,
      'nextArgumentInSourceId': ArgsmeToken.CTX_NEXT_ID,
      'id': ArgsmeToken.ID,
      'conclusion': ArgsmeToken.CONCLUSION,
    }
    self.standalone_keywords = {
      'premises',
      'context'
    }
    
  def extract_tokens(self, lexer):
    lexer.skip_whitespace()

    if lexer.cur_char == '\0':
      return lexer.tokens.append(Token('', ArgsmeToken.EOF))
    
    if lexer.cur_char == '"':
      token = self.handle_keyword(lexer)
      if token.type != ArgsmeToken.UNKNOWN:
        return lexer.tokens.append(token)
    
    lexer.next_char()

  def handle_keyword(self, lexer):
    keyword = lexer.string_lookahead()

    if self.standalone_keyword(keyword):
      return Token(keyword, self.keywords_map[keyword])
    elif self.keyword_with_value(keyword):
      return Token(self.keyword_value(lexer), self.keywords_map[keyword])
    
    return Token(keyword, ArgsmeToken.UNKNOWN)
  
  def standalone_keyword(self, keyword):
    return keyword in self.standalone_keywords

  def keyword_with_value(self, keyword):
    return keyword in self.keywords_map
  
  def keyword_value(self, lexer):
    keyword_value = ''

    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      lexer.next_char()
    lexer.next_char() # Skip the opening quote

    while lexer.cur_char != '"' and lexer.cur_char != '\0':
      keyword_value += lexer.cur_char
      lexer.next_char()
      if lexer.cur_char == '\0':
        lexer.abort('String literal not terminated')

    lexer.next_char()
    return keyword_value.strip()
  
  def tokenize(self, lexer):
    while True:
      self.extract_tokens(lexer)
      if lexer.tokens and lexer.tokens[-1].type == ArgsmeToken.EOF:
        break

    return lexer.tokens