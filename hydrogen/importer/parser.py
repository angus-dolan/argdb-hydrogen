from .models.tokens import ArgsmeToken
from .builder import SadfaceBuilder
from abc import ABC, abstractmethod
import uuid
import hashlib


class BaseParser(ABC):
    def __init__(self):
        pass

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

    def parse(self):
        return self._parser_strategy.parse()


class ArgsmeParser(BaseParser):
    def __init__(self, batch=None, lexed_tokens=None):
        super().__init__()
        self._builder = SadfaceBuilder()
        self._batch = batch
        self._lexed_tokens = lexed_tokens
        self._current_state = 'start'
        self.STATE_TRANSITIONS = {
            'start': '',
            'new_doc': self.meta_core,
            'update_doc': self.build_edge,
            'meta_core': 'end',
            'build_edge': 'end'
        }

    def set_batch(self, batch):
        self._batch = batch

    def set_tokens(self, lexed_tokens):
        self._lexed_tokens = lexed_tokens

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

    def build_edge(self):
        edge = {
          "source_id": self._lexed_tokens[ArgsmeToken.CTX_PREV_ID],
          "target_id": self._lexed_tokens[ArgsmeToken.ID]
        }
        self._builder.with_edge(edge)
        self._current_state = 'end'

    def meta_core(self):
        self._builder.with_meta_core("id", self._lexed_tokens[ArgsmeToken.CTX_SRC_ID])
        self._builder.with_meta_core("created", self._lexed_tokens[ArgsmeToken.CTX_ACQ_TIME])
        self._builder.with_meta_core("edited", self._lexed_tokens[ArgsmeToken.CTX_ACQ_TIME])
        self._builder.with_meta_core("title", self._lexed_tokens[ArgsmeToken.CTX_TITLE])
        self._current_state = 'end'

    def restore(self):
        src_id = self._lexed_tokens[ArgsmeToken.CTX_SRC_ID]
        document = self._batch.completed[src_id]
        new_document = document is None

        if new_document:
            self._current_state = 'new_doc'
            return

        self._builder.with_existing_document(document)
        self._current_state = 'update_doc'

    def process(self):
        if self._current_state == 'start':
            self.restore()
            self.build_node()
        elif self._current_state == 'end':
            return

        next_state = self.STATE_TRANSITIONS.get(self._current_state)
        next_state()

        self.process()

    def parse(self):
        self.process()

        parsed_document = (self._builder.build())
        # valid, error_messages = self._builder.validate()

        # if valid:
        return parsed_document
        # else:
        #   parser.abort(f"Document is not valid. Errors: {error_messages}")
