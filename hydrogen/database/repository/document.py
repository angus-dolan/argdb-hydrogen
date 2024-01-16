from database.models import Document

class DocumentRepository():
  def __init__(self, session):
    self.session = session

  def add(self, document: Document):
    self.session.add(document)
    self.session.commit()

  def find_by_id(self, id):
    pass