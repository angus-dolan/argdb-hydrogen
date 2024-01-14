from data_importer import DataImporter
from database import DocumentDB
from config import Config

if __name__ == "__main__":
  config = Config()
  config = config.get_active()

  importer = DataImporter()
  importer.import_file()