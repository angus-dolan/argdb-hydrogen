import enum

class Token:   
  def __init__(self, token_value, token_type):
    self.value = token_value
    self.type = token_type

class ArgsmeToken(enum.Enum):
  EOF = -1
  PREMISES = ['premises']
  PREMISES_TEXT = ['premises', 'text']
  PREMISES_STANCE = ['premises', 'stance']
  CTX = ['context']
  CTX_SRC_ID = ['context', 'sourceId']
  CTX_PREV_ID = ['context', 'previousArgumentInSourceId']
  CTX_ACQ_TIME = ['context', 'acquisitionTime']
  CTX_TITLE = ['context', 'discussionTitle']
  CTX_SRC_TITLE = ['context', 'sourceTitle']
  CTX_SRC_URL = ['context', 'sourceUrl']
  CTX_NEXT_ID = ['context', 'nextArgumentInSourceId']
  ID = ['id']
  CONCLUSION = ['conclusion']