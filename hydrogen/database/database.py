from config import Config
import sqlite3

class Database:
  def __init__(self):
    self.config = Config()
    self.initialize()

  def initialize(self):
    dbname = self.config.get('datastore', 'name')
    db = sqlite3.connect(dbname + '.sqlite3')
    cursor = db.cursor()

    document_schema = 'id INTEGER PRIMARY KEY'
    self._init_table(db, cursor, 'document', document_schema)

  def _init_table(self, db, cursor, table_name, table_schema):
    try:
      cursor.executescript(f'''
        CREATE TABLE IF NOT EXISTS {table_name}
        (
          {table_schema}
        );
      ''')
      db.commit()
    except Exception as e:
      print(f"An error occurred: {e}")
