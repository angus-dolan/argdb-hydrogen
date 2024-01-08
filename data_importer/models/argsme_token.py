import enum

class ArgsmeToken(enum.Enum):
  EOF = -1
  NEWLINE = 0
  NUMBER = 1
  IDENT = 2
  STRING = 3
  # JSON-specific tokens
  CURLY_OPEN = 4
  CURLY_CLOSE = 5
  SQUARE_OPEN = 6
  SQUARE_CLOSE = 7
  COLON = 8
  COMMA = 9
  # Debate-specific keywords
  PREMISES = 101
  PREMISES_TEXT = 102
  PREMISES_STANCE = 103