from log_config import setup_logging
from config import Config
from database import Database
from importer import ArgsmeBatchImporter
import logging

config = Config()
database = Database()

setup_logging('hydrogen.log')  

if __name__ == "__main__":
  config.initialize()
  database.initialize()

  importer = ArgsmeBatchImporter('./importer/example_data/broken.json')
  importer.batch_import()