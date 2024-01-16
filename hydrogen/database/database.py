from .repository.document import schema as document_schema
from .repository.node import schema as node_schema
from .repository.edge import schema as edge_schema
from config import Config
import sqlite3

class Database:
  def __init__(self):
    self.config = Config()
    self.initialize()

  def initialize(self):
    dbname = self.config.get('datastore', 'name')
    conn = sqlite3.connect(dbname + '.sqlite3')
    cursor = conn.cursor()

    self._init_table(conn, cursor, 'document', document_schema)
    self._init_table(conn, cursor, 'node', node_schema)
    self._init_table(conn, cursor, 'edge', edge_schema)

  def _init_table(self, conn, cursor, table_name, table_schema):
    try:
      cursor.executescript(f'''
        CREATE TABLE IF NOT EXISTS {table_name}
        (
          {table_schema}
        );
      ''')
      conn.commit()
    except Exception as e:
      print(f"An error occurred: {e}")
