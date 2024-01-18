from database import Database, db, Document
from config import Config
from data_importer import DataImporter

config = Config()
database = Database()

if __name__ == "__main__":
  config.initialize()
  database.initialize()

  importer = DataImporter()
  importer.import_file()

  # document1 = Document()
  # db.document.add(document1)