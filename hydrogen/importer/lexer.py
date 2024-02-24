from abc import ABC, abstractmethod
from .models import *
import logging

logger = logging.getLogger(__name__)


class BaseLexer(ABC):
    def __init__(self):
        self._lexed_tokens = {}

    def get_lexed_tokens(self):
        return self._lexed_tokens

    @abstractmethod
    def tokenize(self):
        pass


class Lexer:
    def __init__(self, lexer_strategy: BaseLexer):
        self._lexer_strategy = lexer_strategy

    def set_lexer_strategy(self, lexer_strategy):
        self._lexer_strategy = lexer_strategy

    def get_lexed_tokens(self):
        return self._lexer_strategy.get_lexed_tokens()

    def tokenize(self):
        return self._lexer_strategy.tokenize()


class ArgsmeLexer(BaseLexer):
    def __init__(self, json_data=None):
        super().__init__()
        self._json_data = json_data
        self._current_state = 'start'
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
                ArgsmeToken.CTX_NEXT_ID,
                ArgsmeToken.CTX_TITLE
            ],
            'id': [ArgsmeToken.ID],
            'conclusion': [ArgsmeToken.CONCLUSION]
        }

    def set_argument(self, json_data):
        self._json_data = json_data

    def _process(self):
        next_state = self.STATE_TRANSITIONS.get(self._current_state)
        if next_state == 'end':
            self._current_state = 'end'
            return

        self._current_state = next_state

        for token in self.STATE_TOKENS[self._current_state]:
            nested_keys = token.value
            value = self._get_token_value(nested_keys)
            self._lexed_tokens[token] = value

        self._process()

    def _get_token_value(self, nested_keys):
        try:
            root = self._json_data[nested_keys[0]]

            if len(nested_keys) == 1:
                return root

            value = self._json_data
            for key in nested_keys:
                value = value[key]

            return value
        except Exception as e:
            self._abort(f"Lexer: couldn't get token value {e}")

    def _abort(self, error_message):
        self._current_state = 'end'
        raise Exception(error_message)

    def tokenize(self):
        self._process()
        return self._lexed_tokens
