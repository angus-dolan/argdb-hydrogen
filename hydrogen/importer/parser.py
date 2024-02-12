from .models.tokens import Token, ArgsmeToken
from .builder import SadfaceBuilder
from abc import ABC, abstractmethod
import sys
import uuid
import hashlib
import json


class BaseParser(ABC):
    def __init__(self):
        self._parsed_sf_doc = None

    def get_parsed_sf_doc(self):
        return self._parsed_sf_doc

    def _string_to_uuid(string):
        if string == "":
            return ""
        hashed = hashlib.sha1(string.encode()).hexdigest()
        shortened = hashed[:32]
        return str(uuid.UUID(shortened))

    @abstractmethod
    def parse(self):
        pass


class Parser:
    def __init__(self, parser_strategy: BaseParser):
        self._parser_strategy = parser_strategy

    def set_parser_strategy(self, parser_strategy: BaseParser):
        self._parser_strategy = parser_strategy

    def get_parsed_sf_doc(self):
        return self._parser_strategy.get_parsed_sf_doc()

    def parse(self):
        return self._parser_strategy.parse()


class ArgsmeParser(BaseParser):
    def __init__(self, lexed_tokens):
        super().__init__()
        self._builder = SadfaceBuilder()
        self._lexed_tokens = lexed_tokens
        self._current_state = 'start'
        self.STATE_TRANSITIONS = {
            'start': self.build_node,
            'update_or_new': self.decide_update_or_new,
            'new_doc': self.meta_core,
            'update_doc': self.build_edge,
            'meta_core': 'end',
            'build_edge': 'end'
        }

    def decide_update_or_new(self):
        if self._lexed_tokens[ArgsmeToken.CTX_PREV_ID]:
            self._current_state = 'update_doc'
        else:
            self._current_state = 'new_doc'

    def build_node(self):
        node = {
            "id": self._lexed_tokens[ArgsmeToken.ID],
            "metadata": {
                "stance": self._lexed_tokens[ArgsmeToken.PREMISES_STANCE],
            },
            "text": self._lexed_tokens[ArgsmeToken.PREMISES_TEXT],
            "type": "atom",
        }
        self._builder.with_node(node)
        self._current_state = 'update_or_new'

    def build_edge(self):
        edge = {
          "source_id": self._lexed_tokens[ArgsmeToken.CTX_PREV_ID],
          "target_id": self._lexed_tokens[ArgsmeToken.CTX.CTX_NEXT_ID]
        }
        self._builder.with_edge(edge)
        self._current_state = 'end'

    def meta_core(self):
        self._builder.with_metadata_core("id", self._lexed_tokens[ArgsmeToken.CTX_SRC_ID])
        self._builder.with_metadata_core("created", self._lexed_tokens[ArgsmeToken.CTX_ACQ_TIME])
        self._builder.with_metadata_core("edited", self._lexed_tokens[ArgsmeToken.CTX_ACQ_TIME])
        self._builder.with_metadata_core("title", self._lexed_tokens[ArgsmeToken.CTX_TITLE])
        self._current_state = 'end'

    def process(self):
        if self._current_state == 'end':

            return
        next_state = self.STATE_TRANSITIONS.get(self._current_state)

        next_state()
        self.process()

    def parse(self):
        self.process()
        print('')
