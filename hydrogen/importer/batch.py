from abc import ABC, abstractmethod
import logging
import json
import ijson
import sys
import os

logger = logging.getLogger(__name__)


def _abort(message):
    print(message)
    logger.exception(message)
    sys.exit()


class BaseImporter(ABC):
    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def batch_import(self):
        pass


class ArgsmeBatchImporter(BaseImporter):
    def __init__(self, file_path, batch_size_bytes=1073741824):
        super().__init__(file_path)
        self.batch_size_bytes = batch_size_bytes  # 1GB

    def batch_import(self):
        if not os.path.exists(self.file_path):
            _abort(f"File does not exist: {self.file_path}")

        self._load_batches()

    def _load_batches(self):
        current_batch = []
        current_batch_size = 0

        try:
            with open(self.file_path, 'rb') as file:
                arguments = ijson.items(file, 'arguments.item')

                for argument in arguments:
                    argument_str = json.dumps(argument)
                    argument_size = len(argument_str.encode('utf-8'))

                    if current_batch_size + argument_size > self.batch_size_bytes:
                        self._process_batch(current_batch)
                        # Start a new batch
                        current_batch = [argument]
                        current_batch_size = argument_size
                    else:
                        current_batch.append(argument)
                        current_batch_size += argument_size

                # Enqueue the last batch if it has any arguments
                if current_batch:
                    self._process_batch(current_batch)

        except Exception as e:
            _abort(f"Failed to load batches: {e}")

    def _process_batch(self, batch):
        pass
