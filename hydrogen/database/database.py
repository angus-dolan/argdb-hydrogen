from database.repository.document import DocumentRepository
from database.connection import *

class Database:
  def __init__(self):
    self.session = Session()
    self.document = DocumentRepository(self.session)

  def initialize(self):
    Base.metadata.create_all(bind=engine)

db = Database()
