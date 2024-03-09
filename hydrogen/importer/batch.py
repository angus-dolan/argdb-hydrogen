from .lexer import ArgsmeLexer
from .parser import ArgsmeParser
from .emitter import Emitter
from collections import deque
from abc import ABC, abstractmethod
import logging
import json
import ijson
import os

logger = logging.getLogger(__name__)


# TODO: Investigate Stream-Based Processing and Filtering at Parse Time with ijson to improve performance
# TODO: Remove not handling multiple batches tech debt, current implementation only works with 1 batch

class BaseImporter(ABC):
    def __init__(self, file_path):
        self.file_path = file_path
        self.emitter = Emitter()

    def get_file_path(self):
        return self.file_path

    def abort(self, message):
        print(message)
        logger.exception(message)

    @abstractmethod
    def batch_import(self):
        pass


class ArgsmeBatchImporter(BaseImporter):
    def __init__(self, file_path, batch_size_bytes=1073741824):
        super().__init__(file_path)
        self.batch_size_bytes = batch_size_bytes  # 1GB
        self.pending = deque()
        self.completed = {}
        self.failed = {}

    def init_batch(self):
        self.pending.clear()
        self.completed.clear()
        self.failed.clear()

    def add_pending_argument(self, pending_arg):
        src_id = pending_arg['context']['sourceId']
        self.pending.append(pending_arg)

        if src_id not in self.completed:
            self.completed[src_id] = None

    def get_completed_arguments(self):
        return self.completed

    def get_completed_argument(self, src_id):
        return self.completed[src_id]

    def has_pending(self):
        return len(self.pending) > 0

    def process(self):
        while self.pending:
            argument = self.pending.popleft()

            try:
                lexer = ArgsmeLexer(json_data=argument)
                lexer.tokenize()
                tokens = lexer.get_lexed_tokens()
                parser = ArgsmeParser(batch=self, lexed_tokens=tokens)
                sadface = parser.parse()
                self.completed[sadface.get_id()] = sadface.document

            except Exception as e:
                # TODO: Add to self.failed
                print(f"Failed processing document: {e}")

    def batch_import(self):
        if not os.path.exists(self.file_path):
            self.abort(f"File does not exist: {self.file_path}")

        self.init_batch()
        current_batch_size = 0

        try:
            with open(self.file_path, 'rb') as file:
                arguments = ijson.items(file, 'arguments.item')

                for argument in arguments:
                    argument_str = json.dumps(argument)
                    argument_size = len(argument_str.encode('utf-8'))
                    new_batch = current_batch_size + argument_size > self.batch_size_bytes

                    if new_batch:
                        self.process()
                        self.init_batch()
                        self.add_pending_argument(argument)
                        current_batch_size = argument_size
                    else:
                        self.add_pending_argument(argument)
                        current_batch_size += argument_size

                # Process any remaining
                if self.has_pending():
                    self.process()

        except Exception as e:
            self.abort(f"Failed to load batches: {e}")

        # Emmit to datastore and search engine
        completed = self.get_completed_arguments()
        for id, argument in completed.items():
            self.emitter.set_uuid(id)
            self.emitter.set_document(argument)
            self.emitter.emit()


