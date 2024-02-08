from .models.tokens import Token, ArgsmeToken
from .builder import SadfaceBuilder
from abc import ABC, abstractmethod
import uuid
import hashlib
import json


class BaseParser(ABC):
    def __init__(self):
        self._parsed_sf_doc = None

    def get_parsed_sf_doc(self):
        return self._parsed_sf_doc

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

    def parse(self):
        pass
