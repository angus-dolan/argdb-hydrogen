from log_config import setup_logging
from config import Config
from database import Database
from data_importer import DataImporter
import logging

config = Config()
database = Database()

setup_logging('hydrogen.log')  

if __name__ == "__main__":
  config.initialize()
  database.initialize()

  importer = DataImporter('./data_importer/example_data/args-me.json')
  importer.import_file()