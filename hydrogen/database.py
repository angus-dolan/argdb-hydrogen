from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from abc import ABC, abstractmethod
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from config import Config

config = Config()
database_name = config.get('datastore', 'name')
database_url = f"sqlite:///{database_name}.sqlite3"
engine = create_engine(database_url, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

'''
    Databases and Tables:

    argdb.sqlite: A SQLite database designed to manage argument data and import operations.
    - `arguments`: Contains the full argument records.
    - `importer_failed`: Logs arguments where the import process encountered errors.
    - `importer_lq`: Arguments that are greater than 210 characters are deemed low quality, thus not search indexed.
'''

# TODO: Implement importer_failed and importer_lq persistence in importer

class Arguments(Base):
    __tablename__ = 'arguments'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    data = Column(String)


class ImporterFailed(Base):
    __tablename__ = 'importer_failed'
    id = Column(Integer, primary_key=True)
    error_detail = Column(Text)


class ImporterLQ(Base):
    __tablename__ = 'importer_lq'
    id = Column(Integer, primary_key=True)
    argument_id = Column(Integer)


class BaseRepository(ABC):
    def __init__(self, session, model):
        self.session = session
        self.model = model

    @abstractmethod
    def add(self, **kwargs):
        pass

    @abstractmethod
    def get(self, **kwargs):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass

    @abstractmethod
    def delete(self, **kwargs):
        pass

    @contextmanager
    def managed_transaction(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class ArgumentsRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Arguments)

    def add(self, **kwargs):
        payload = kwargs['payload']
        with self.managed_transaction():
            self.session.add(payload)

    def get(self, **kwargs):
        uuid = kwargs['uuid']
        return self.session.query(self.model).filter_by(uuid=uuid).one_or_none()

    def get_all(self):
        return self.session.query(self.model).all()

    def update(self, **kwargs):
        uuid, payload = kwargs['uuid'], kwargs['payload']

        with self.managed_transaction():
            item = self.get(uuid=uuid)
            if item:
                item.data = payload
                self.session.add(item)

    def delete(self, **kwargs):
        uuid = kwargs['uuid']
        with self.managed_transaction():
            item = self.get(uuid=uuid)
            if item:
                self.session.delete(item)


class ImporterFailedRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, ImporterFailed)

    def add(self, **kwargs):
        payload = kwargs['payload']
        with self.managed_transaction():
            self.session.add(payload)

    def get(self, **kwargs):
        id = kwargs['id']
        return self.session.query(self.model).filter_by(id=id).one_or_none()

    def get_all(self):
        return self.session.query(self.model).all()

    def update(self, **kwargs):
        id, payload = kwargs['id'], kwargs['payload']
        with self.managed_transaction():
            item = self.get(id=id)
            if item:
                item.error_detail = payload['error_detail']
                self.session.add(item)

    def delete(self, **kwargs):
        id = kwargs['id']
        with self.managed_transaction():
            item = self.get(id=id)
            if item:
                self.session.delete(item)


class ImporterLQRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, ImporterLQ)

    def add(self, **kwargs):
        payload = kwargs['payload']
        with self.managed_transaction():
            self.session.add(payload)

    def get(self, **kwargs):
        id = kwargs['id']
        return self.session.query(self.model).filter_by(id=id).one_or_none()

    def get_all(self):
        return self.session.query(self.model).all()

    def update(self, **kwargs):
        id, payload = kwargs['id'], kwargs['payload']
        with self.managed_transaction():
            item = self.get(id=id)
            if item:
                item.argument_id = payload['argument_id']
                self.session.add(item)

    def delete(self, **kwargs):
        id = kwargs['id']
        with self.managed_transaction():
            item = self.get(id=id)
            if item:
                self.session.delete(item)


class Database:
    def __init__(self):
        self.session = Session()
        self.arguments = ArgumentsRepository(self.session)
        self.importer_failed = ImporterFailedRepository(self.session)
        self.importer_lq = ImporterLQRepository(self.session)

    def initialize(self):
        Base.metadata.create_all(bind=engine)
