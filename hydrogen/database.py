from sqlalchemy import create_engine, Column, Integer, String
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


class Raw(Base):
    __tablename__ = 'raw'
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True)
    data = Column(String)


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


class RawRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Raw)

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


class Database:
    def __init__(self):
        self.session = Session()
        self.raw = RawRepository(self.session)

    def initialize(self):
        Base.metadata.create_all(bind=engine)
