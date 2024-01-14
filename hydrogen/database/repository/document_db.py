import sqlite3

class DocumentDB:
  def __init__(self, db_path):
    self.db_path = db_path
    self.conn = sqlite3.connect(self.db_path)
    self._create_table()

  def _create_table(self):
    try:
      self.conn.execute('''
        CREATE TABLE IF NOT EXISTS documents (
          id INTEGER PRIMARY KEY
        )
      ''')
      self.conn.commit()
    except Exception as e:
      print(f"An error occurred: {e}")

  def add_document(self):
    try:
      with self.conn:
        self.conn.execute('INSERT INTO documents DEFAULT VALUES')
        return self.conn.lastrowid # id
    except sqlite3.IntegrityError as e:
      print(f"An error occurred: {e}")
      return None
