from config import Config
from database import Database
from data_importer import DataImporter

config = Config()
database = Database()

if __name__ == "__main__":
  config.initialize()
  database.initialize()

  importer = DataImporter('./data_importer/example_data/args-me.json')
  importer.import_file()