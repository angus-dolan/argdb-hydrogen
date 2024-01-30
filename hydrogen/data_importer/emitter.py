from database import Database, Raw
import json 

db = Database()

class Emitter:
  def __init__(self, uuid, doc):
    self.document = doc
    self.uuid = uuid

  def set_uuid(self, uuid):
    self.uuid = uuid

  def set_document(self, doc):
    self.document = doc

  def emit(self):
    result = db.raw.get(self.uuid)
    
    if result:
      return db.raw.update(self.uuid, json.dumps(self.document))
    
    return db.raw.add(Raw(uuid=self.uuid, data=json.dumps(self.document)))
    
    