from .lexer import Lexer, ArgsmeLexer
from abc import ABC, abstractmethod
from helpers.timer import Timer
import logging
import pyjq
import json
import sys
import os

logger = logging.getLogger(__name__)


class BaseImporter(ABC):
    def __init__(self, file_path):
        self.file_path = file_path

    def abort(self, message):
        logger.exception(message)
        sys.exit()

    @abstractmethod
    def batch_import(self):
        pass


class ArgsmeBatchImporter(BaseImporter):
    def __init__(self, file_path, batch_size=1000):
        super().__init__(file_path)
        self.json = self.load_json()
        self.batch_size = batch_size
        self.num_args = 0
        self.num_batches = 0
        self.calculate_batch_parameters()

    def load_json(self):
        if not os.path.exists(self.file_path):
            self.abort(f"File does not exist: {self.file_path}")
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def calculate_batch_parameters(self):
        self.num_args = pyjq.first('.arguments | length', self.json)
        if self.num_args == 0:
            self.abort("No arguments found in file")
        self.num_batches = -(-self.num_args // self.batch_size)

    def batch_import(self):
        try:
            with Timer() as timer:
                for batch_num in range(self.num_batches):
                    start_index = batch_num * self.batch_size
                    end_index = min(start_index + self.batch_size, self.num_args)
                    logger.info(f"Importing arguments {start_index} to {end_index} of {self.num_args}")

                    for i in range(start_index, end_index):
                        argument = pyjq.first(f".arguments[{i}]", self.json)

                        lexer = Lexer(ArgsmeLexer(argument))
                        lexer.tokenize_argument()

            logger.info(f"Batch imported {self.num_args} arguments. Total time: {timer.elapsed} seconds")
        except Exception as e:
            self.abort(f"Failed to import data: {e}")
