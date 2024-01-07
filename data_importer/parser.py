from abc import ABC, abstractmethod

class ParserStrategy(ABC):
  @abstractmethod
  def parse(self, tokens):
    pass

class Parser:
  def __init__(self, parser_strategy: ParserStrategy):
    self._parser_strategy = parser_strategy

  def set_parser_strategy(self, parser_strategy: ParserStrategy):
    self._parser_strategy = parser_strategy

  def parse_tokens(self, tokens):
    return self._parser_strategy.parse(tokens)

class ArgsmeParser(ParserStrategy): 
  def parse(self, tokens):
    # TODO: Use the argument builder to build an argument
    # ...
    pass
