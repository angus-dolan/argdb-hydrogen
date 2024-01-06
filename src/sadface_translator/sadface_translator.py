from .lexer import Lexer
from .parser import Parser
from .emitter import Emitter

class SadfaceTranslator:
  def __init__(self, input_data):
    self.input = input_data

  def translate(self):
    lexer = Lexer(self.input)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    parsed_data = parser.parse()

    emitter = Emitter(parsed_data)
    return emitter.emit()

# Example usage
if __name__ == "__main__":
  translator = SadfaceTranslator("input data here")
  result = translator.translate()
  print(result)
