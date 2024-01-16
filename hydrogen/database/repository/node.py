schema = '''
  id INTEGER PRIMARY KEY, 
  document_id INTEGER, 
  text TEXT,
  type TEXT,
  FOREIGN KEY(document_id) 
  REFERENCES document(id)
'''

class NodeDB:
  pass
