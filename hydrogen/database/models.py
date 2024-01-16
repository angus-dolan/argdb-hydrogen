from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from database.connection import Base

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
