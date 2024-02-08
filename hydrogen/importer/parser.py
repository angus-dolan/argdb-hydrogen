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
    def __init__(self, lexed_tokens: list):
        super().__init__()
        self._lexed_tokens = lexed_tokens
        self._current_state = 'start'
        # TODO: Return lexed_tokens from lexer as a hashmap with ArgsmeToken as key, for O(1)
        # NOTE: Maybe the state transitions should be 'build_new_doc', 'update_existing_doc' etc.
        # NOTE: Think about mem management, if I've got 1GB in mem, I could end up needing an another GB unless I free the memory as we parse.
        self.DYNAMIC_TRANSITIONS = {
            'update_or_new': self.decide_update_or_new,
            'another_state': self.decide_for_another_state
        }
        self.STATE_TRANSITIONS = {
            'start': 'build_node',
            'build_node': 'update_or_new',
            'update': None,
            'new': None,
        }
        # self.STATE_TRANSITIONS = {
        #     'start': 'premises_stance',
        #     'premises_stance': 'premises_text',
        #     'premises_text': 'ctx_acq_time',
        #     'ctx_acq_time': 'ctx_src_id',
        #     'ctx_src_id': 'ctx_prev_id',
        #     'ctx_prev_id': 'ctx_title',
        #     'ctx_title': 'id',
        #     'id': 'conclusion',
        #     'conclusion': 'end'
        # }
        self.STATE_HANDLERS = {
            ArgsmeToken.PREMISES_STANCE: 'premises_stance',
        }

    def parse(self):
        pass
