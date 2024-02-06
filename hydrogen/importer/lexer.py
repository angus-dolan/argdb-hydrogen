from models.tokens import Token, ArgsmeToken
from abc import ABC, abstractmethod

class BaseLexer(ABC):
  @abstractmethod
  def tokenize(self):
    pass

class Lexer:
  def __init__(self, lexer_strategy: BaseLexer):
    self._lexer_strategy = lexer_strategy

  def set_lexer_strategy(self, lexer_strategy):
    self._lexer_strategy = lexer_strategy
    
  def tokenize_argument(self):
    return self._lexer_strategy.tokenize()

class ArgsmeLexer(BaseLexer):
  def __init__(self, json_data):
    self.json_data = json_data
    self.current_state = 'start'
    # self.STATES = {
    #   'start': self.start_state,
    #   'premises': self.process_premises,
    #   'context': self.process_context,
    #   'id': self.process_id,
    #   'conclusion': self.process_conclusion,
    #   'end': self.end_state,
    #   'error': self.error
    # }
    self.STATE_TRANSITIONS = {
      'start': 'premises',
      'premises': 'context',
      'context': 'id',
      'id': 'conclusion',
      'conclusion': 'end',
      'end': 'start'
    }
    self.TOKENS = {
      'premises': [
        ArgsmeToken.PREMISES_STANCE, 
        ArgsmeToken.PREMISES_TEXT
      ],
      'context': [
        ArgsmeToken.CTX_ACQ_TIME, 
        ArgsmeToken.CTX_SRC_ID,
        ArgsmeToken.CTX_PREV_ID,
        ArgsmeToken.CTX_TITLE
      ],
      'id': [ArgsmeToken.ID],
      'conclusion': [ArgsmeToken.CONCLUSION]
    }
    self.tokens = []

  def access_nested_json(self, keys):
    value = self.json_data
    for key in keys:
      try:
        value = value[key]
      except KeyError:
        self.error(f"Key '{key}' not found in JSON data.")
        return None
    return value

  def process(self):
    if self.current_state == 'end':
      return
    
    self.current_state = self.STATE_TRANSITIONS[self.current_state]
    for token in self.TOKENS[self.current_state]:
      value = self.json_data['context']
      value = self.json_data['context']['sourceId']
      self.tokens.append(Token(self.json_data[self.current_state][token], token))
    self.process()

  def error(self, error_message):
    print("Error:", error_message)
    self.current_state = 'end'

  def start_state(self):
    self.current_state = 'premises'
    self.STATES[self.current_state]()

  def process_premises(self):
    # self.premises = self.json_data['premises']
    self.current_state = 'context'
    self.STATES[self.current_state]()

  def process_context(self):
    # self.context = self.json_data['context']
    self.current_state = 'id'
    self.STATES[self.current_state]()

  def process_id(self):
    # self.id = self.json_data['id']
    self.current_state = 'conclusion'
    self.STATES[self.current_state]()

  def process_conclusion(self):
    # self.conclusion = self.json_data['conclusion']
    self.current_state = 'end'
    self.STATES[self.current_state]()

  def end_state(self):
    self.current_state = 'start' # Reset to start for potential reuse

  def tokenize(self):
    # self.STATES[self.current_state]()
    self.process()
    print(self.tokens)
