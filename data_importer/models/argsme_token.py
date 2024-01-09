import enum

class ArgsmeToken(enum.Enum):
  EOF = -1
  NEWLINE = 0
  UNKNOWN = 1
  STRING = 2
  # JSON-specific tokens
  CURLY_OPEN = 4
  CURLY_CLOSE = 5
  SQUARE_OPEN = 6
  SQUARE_CLOSE = 7
  COLON = 8
  COMMA = 9
  # Argsme-specific tokens
  PREMISES = 101
  PREMISES_TEXT = 102
  PREMISES_STANCE = 103
  CTX = 104
  CTX_SRC_ID = 105
  CTX_PREV_ID = 106
  CTX_ACQ_TIME = 107
  CTX_TITLE = 108
  CTX_SRC_TITLE = 109
  CTX_SRC_URL = 110
  CTX_NEXT_ID = 111
  ID = 112
  CONCLUSION = 113