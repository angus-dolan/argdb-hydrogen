from contextlib import contextmanager
from hydrogen.database.schema import Raw

class RawRepository:
  def __init__(self, session):
    self.session = session

  def insert_one(self, raw: Raw):
    with self.managed_transaction():
      self.session.add(raw)

  # def find_by_id(self, raw_id):
  #   return self.session.query(Raw).filter_by(id=raw_id).one_or_none()

  @contextmanager
  def managed_transaction(self):
    try:
      yield
      self.session.commit()
    except Exception:
      self.session.rollback()
      raise
