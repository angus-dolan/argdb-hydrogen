from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from config import Config

config = Config()
database_name = config.get('datastore', 'name')
database_url = f"sqlite:///{database_name}.sqlite3"
engine = create_engine(database_url, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Raw(Base):
  __tablename__ = 'raw'
  id = Column(Integer, primary_key=True)
  uuid = Column(String)
  data = Column(String)

class Document(Base):
  __tablename__ = 'document'
  id = Column(Integer, primary_key=True)

class Node(Base):
  __tablename__ = 'node'
  id = Column(Integer, primary_key=True)
  document_id = Column(Integer, ForeignKey('document.id'))
  text = Column(String)
  type = Column(String)

class Edge(Base):
  __tablename__ = 'edge'
  id = Column(Integer, primary_key=True)
  source_id = Column(Integer, ForeignKey('node.id'))
  target_id = Column(Integer, ForeignKey('node.id'))

class MetaCore(Base):
  __tablename__ = 'meta_core'
  id = Column(Integer, primary_key=True)
  document_id = Column(Integer, ForeignKey('document.id'))
  analyst_name = Column(String)
  analyst_email = Column(String)
  created = Column(DateTime)
  edited = Column(DateTime)

class BaseRepository:
  def __init__(self, session, model):
    self.session = session
    self.model = model

  def add(self, item):
    with self.managed_transaction():
      self.session.add(item)

  def get(self, id):
    return self.session.query(self.model).filter_by(id=id).one_or_none()

  def get_all(self):
    return self.session.query(self.model).all()

  def update(self):
    with self.managed_transaction():
      pass

  def delete(self, id):
    with self.managed_transaction():
      item = self.get(id)
      if item:
        self.session.delete(item)

  @contextmanager
  def managed_transaction(self):
    try:
      yield
      self.session.commit()
    except Exception as e:
      self.session.rollback()
      raise e
    
class DocumentRepository(BaseRepository):
  def __init__(self, session):
    super().__init__(session, Document)

class RawRepository(BaseRepository):
  def __init__(self, session):
    super().__init__(session, Raw)
  
  def get(self, uuid):
    return self.session.query(self.model).filter_by(uuid=uuid).one_or_none()

class Database:
  def __init__(self):
    self.session = Session()
    self.raw = RawRepository(self.session)
    self.document = DocumentRepository(self.session)

  def initialize(self):
    Base.metadata.create_all(bind=engine)
