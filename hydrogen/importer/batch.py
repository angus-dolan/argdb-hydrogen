from .lexer import ArgsmeLexer
from .parser import ArgsmeParser
from collections import deque
from abc import ABC, abstractmethod
import logging
import json
import ijson
import os

logger = logging.getLogger(__name__)


# TODO: Investigate Stream-Based Processing and Filtering at Parse Time with ijson to improve performance


class BaseImporter(ABC):
    def __init__(self, file_path):
        self.file_path = file_path

    def get_file_path(self):
        return self.file_path

    def abort(self, message):
        print(message)
        logger.exception(message)

    @abstractmethod
    def batch_import(self):
        pass


class ArgsmeBatchImporter(BaseImporter):
    class Batch:
        def __init__(self):
            self.pending = deque()
            self.completed = {}
            self.failed = {}

        def init_current_batch(self):
            self.pending.clear()
            self.completed.clear()
            self.failed.clear()

        def add_pending_argument(self, pending_arg):
            src_id = pending_arg['context']['sourceId']
            if src_id not in self.completed:
                self.completed[src_id] = None
            self.pending.append(pending_arg)

        def get_completed_argument(self, src_id):
            return self.completed

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

    def __init__(self, file_path, batch_size_bytes=1073741824):
        super().__init__(file_path)
        self.batch_size_bytes = batch_size_bytes  # 1GB
        self.current_batch = self.Batch()

    def batch_import(self):
        if not os.path.exists(self.file_path):
            self.abort(f"File does not exist: {self.file_path}")

        self.load_argsme_batches()

    def load_argsme_batches(self):
        current_batch_size = 0
        self.current_batch.init_current_batch()

        try:
            with open(self.file_path, 'rb') as file:
                arguments = ijson.items(file, 'arguments.item')

                for argument in arguments:
                    argument_str = json.dumps(argument)
                    argument_size = len(argument_str.encode('utf-8'))

                    if current_batch_size + argument_size > self.batch_size_bytes:
                        self.current_batch.process()
                        self.current_batch.init_current_batch()
                        self.current_batch.add_pending_argument(argument)
                        current_batch_size = argument_size
                    else:
                        self.current_batch.add_pending_argument(argument)
                        current_batch_size += argument_size

                # Process any remaining
                if self.current_batch.has_pending():
                    self.current_batch.process()

        except Exception as e:
            self.abort(f"Failed to load batches: {e}")
