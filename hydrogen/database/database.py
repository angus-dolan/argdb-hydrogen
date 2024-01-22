from database.repository.document import DocumentRepository
from database.repository.raw import RawRepository
from database.connection import *

class Database:
  def __init__(self):
    self.session = Session()
    self.raw = RawRepository(self.session)
    self.document = DocumentRepository(self.session)

  def initialize(self):
    Base.metadata.create_all(bind=engine)

db = Database()
