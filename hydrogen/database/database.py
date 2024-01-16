from database.repository.document import DocumentRepository
from database.connection import Session

class Database:
  def __init__(self):
    self.session = Session()
    self.document = DocumentRepository(self.session)

db = Database()
