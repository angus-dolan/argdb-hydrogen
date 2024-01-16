from database.database import db
from database.models import Document

from config import Config
from data_importer import DataImporter

if __name__ == "__main__":
  config = Config()
  
  document1 = Document()
  db.document.add(document1)



  # importer = DataImporter()
  # importer.import_file()

  # doc_db = DocumentDB()
  # doc_db.add_document()