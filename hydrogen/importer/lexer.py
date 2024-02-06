from abc import ABC, abstractmethod
from .models import *
from collections import deque
import logging

logger = logging.getLogger(__name__)

class BaseLexer(ABC):
    def __init__(self):
        self.lexed_tokens = deque()

    @abstractmethod
    def tokenize(self):
        pass


class Lexer:
    def __init__(self, lexer_strategy: BaseLexer):
        self._lexer_strategy = lexer_strategy

    def set_lexer_strategy(self, lexer_strategy):
        self._lexer_strategy = lexer_strategy

    def get_lexed_tokens(self):
        return self._lexer_strategy.lexed_tokens

    def tokenize_argument(self):
        return self._lexer_strategy.tokenize()


class ArgsmeLexer(BaseLexer):
    def __init__(self, json_data):
        super().__init__()
        self.json_data = json_data
        self.lexed_tokens = deque()
        self.current_state = 'start'
        self.STATE_TRANSITIONS = {
            'start': 'premises',
            'premises': 'context',
            'context': 'id',
            'id': 'conclusion',
            'conclusion': 'end',
        }
        self.STATE_TOKENS = {
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


    def process(self):
        next_state = self.STATE_TRANSITIONS.get(self.current_state)
        if next_state == 'end':
            return

        self.current_state = next_state

        for token in self.STATE_TOKENS[self.current_state]:
            nested_keys = token.value
            value = self.get_token_value(nested_keys)
            self.lexed_tokens.append(Token(value, token))

        self.process()

    def get_token_value(self, nested_keys):
        try:
            root = self.json_data[nested_keys[0]]

            if len(nested_keys) == 1:
                return root

            value = self.json_data
            for key in nested_keys:

                    value = value[key]

            return value
        except Exception as e:
            self.error(f"Lexer: couldn't get token value {e}")

    def error(self, error_message):
        self.current_state = 'end'
        raise Exception(error_message)

    def tokenize(self):
        self.process()
        return self.lexed_tokens
