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
    self.source = source + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement
    self.cur_char = '' # Current character in the string
    self.cur_pos = -1 # Current position in the string
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

  # Return the lookahead character
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

class ArgsmeLexer(LexerStrategy):
  def get_token(self, lexer):
    lexer.skip_whitespace()
    lexer.skip_comment()
    token = None

    # Check the first character of this token to see if we can decide what it is
    # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest
    if lexer.cur_char == '+':
      token = Token(lexer.cur_char, ArgsmeToken.PLUS)
    elif lexer.cur_char == '-':
      token = Token(lexer.cur_char, ArgsmeToken.MINUS)
    elif lexer.cur_char == '*':
      token = Token(lexer.cur_char, ArgsmeToken.ASTERISK)
    elif lexer.cur_char == '/':
      token = Token(lexer.cur_char, ArgsmeToken.SLASH)
    elif lexer.cur_char == '=':
      # Check whether this token is = or ==
      if lexer.peek() == '=':
        last_char = lexer.cur_char
        lexer.next_char()
        token = Token(last_char + lexer.cur_char, ArgsmeToken.EQEQ)
      else:
        token = Token(lexer.cur_char, ArgsmeToken.EQ)
    elif lexer.cur_char == '>':
      # Check whether this is token is > or >=
      if lexer.peek() == '=':
        last_char = lexer.cur_char
        lexer.next_char()
        token = Token(last_char + lexer.cur_char, ArgsmeToken.GTEQ)
      else:
        token = Token(lexer.cur_char, ArgsmeToken.GT)
    elif lexer.cur_char == '<':
      # Check whether this is token is < or <=
      if lexer.peek() == '=':
        last_char = lexer.cur_char
        lexer.next_char()
        token = Token(last_char + lexer.cur_char, ArgsmeToken.LTEQ)
      else:
        token = Token(lexer.cur_char, ArgsmeToken.LT)
    elif lexer.cur_char == '!':
      if lexer.peek() == '=':
        last_char = lexer.cur_char
        lexer.next_char()
        token = Token(last_char + lexer.cur_char, ArgsmeToken.NOTEQ)
      else:
        lexer.abort("Expected !=, got !" + lexer.peek())
    elif lexer.cur_char == '\n':
      token = Token(lexer.cur_char, ArgsmeToken.NEWLINE)
    elif lexer.cur_char == '\0':
      token = Token('', ArgsmeToken.EOF)
    else:
      lexer.abort("Unknown token: " + lexer.cur_char)
      pass
  
    lexer.next_char()
    return token
  
  def tokenize(self, lexer):
    token = self.get_token(lexer)
    while token.kind != ArgsmeToken.EOF:
      print(token.kind)
      token = self.get_token(lexer)

