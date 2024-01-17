from database import Database, db, Document
from config import Config
from data_importer import DataImporter

config = Config()
database = Database()

if __name__ == "__main__":
  config.initialize()
  database.initialize()

  document1 = Document()
  db.document.add(document1)

  importer = DataImporter()
  importer.import_file()