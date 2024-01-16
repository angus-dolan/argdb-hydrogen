from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Load your configuration
config = Config()
database_name = config.get('datastore', 'name')

# Create a connection string for SQLite
database_url = f"sqlite:///{database_name}.sqlite3"

# Create the SQLAlchemy engine
engine = create_engine(database_url, echo=True)

# Set up the sessionmaker
Session = sessionmaker(bind=engine)

# Declarative base
Base = declarative_base()
