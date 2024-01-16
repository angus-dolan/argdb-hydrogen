from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

config = Config()

database_name = config.get('datastore', 'name')
database_url = f"sqlite:///{database_name}.sqlite3"
engine = create_engine(database_url, echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()
