from contextlib import contextmanager
from hydrogen.database.schema import Document

class DocumentRepository:
  def __init__(self, session):
    self.session = session

  def insert_one(self, document: Document):
    with self.managed_transaction():
      self.session.add(document)

  def find_by_id(self, document_id):
    return self.session.query(Document).filter_by(id=document_id).one_or_none()

  @contextmanager
  def managed_transaction(self):
    try:
      yield
      self.session.commit()
    except Exception:
      self.session.rollback()
      raise
