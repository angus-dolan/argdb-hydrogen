from abc import ABC, abstractmethod
import json

class LexerStrategy(ABC):
  @abstractmethod
  def tokenize(self, data):
    pass

class ArgsmeLexer(LexerStrategy):
  def tokenize(self, data):
    try:
      # Tokenizing JSON data
      return data
    except json.JSONDecodeError:
      return "Invalid JSON"

class LexerContext:
  def __init__(self, lexer_strategy: LexerStrategy):
    self._lexer_strategy = lexer_strategy

  def set_lexer_strategy(self, lexer_strategy: LexerStrategy):
    self._lexer_strategy = lexer_strategy

  def tokenize_data(self, data):
    return self._lexer_strategy.tokenize(data)