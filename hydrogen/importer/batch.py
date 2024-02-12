from .lexer import Lexer, ArgsmeLexer
from .parser import Parser, ArgsmeParser
from collections import deque
from abc import ABC, abstractmethod
import logging
import json
import ijson
import os

logger = logging.getLogger(__name__)


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
    def __init__(self, file_path, batch_size_bytes=1073741824):
        super().__init__(file_path)
        self.batch_size_bytes = batch_size_bytes  # 1GB

    def batch_import(self):
        if not os.path.exists(self.file_path):
            self.abort(f"File does not exist: {self.file_path}")

        self.load_argsme_batches()

    def load_argsme_batches(self):
        def init_current_batch():
            return deque()

        current_batch = init_current_batch()
        current_batch_size = 0

        def save_pending_argument(pending_arg):
            current_batch.append(pending_arg)

        # TODO: Investigate Stream-Based Processing and Filtering at Parse Time with ijson to improve performance
        try:
            with open(self.file_path, 'rb') as file:
                arguments = ijson.items(file, 'arguments.item')

                for argument in arguments:
                    argument_str = json.dumps(argument)
                    argument_size = len(argument_str.encode('utf-8'))

                    if current_batch_size + argument_size > self.batch_size_bytes:
                        self.process_argsme_batch(current_batch)
                        # Start a new batch
                        init_current_batch()
                        save_pending_argument(argument)
                        current_batch_size = argument_size
                    else:
                        save_pending_argument(argument)
                        current_batch_size += argument_size

                # Process the last batch if it has any arguments
                if current_batch:
                    self.process_argsme_batch(current_batch)

        except Exception as e:
            self.abort(f"Failed to load batches: {e}")

    def process_argsme_batch(self, batch):
        while batch:
            argument = batch.popleft()

            try:
                lexer = ArgsmeLexer(json_data=argument)
                lexer.tokenize()
                tokens = lexer.get_lexed_tokens()

                parser = ArgsmeParser(lexed_tokens=tokens)
                parser.parse()
                sadface_doc = parser.get_parsed_sf_doc()
            except Exception as e:
                # TODO: Add id to batch['failed']
                print(e)

            # TODO: Print any failures
