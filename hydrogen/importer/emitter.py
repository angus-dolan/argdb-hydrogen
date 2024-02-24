from database import Database, Raw
import json

db = Database()


class Emitter:
    def __init__(self, uuid=None, doc=None):
        self.document = doc
        self.uuid = uuid

    def set_uuid(self, uuid):
        self.uuid = uuid

    def set_document(self, doc):
        self.document = doc

    def emit(self):
        exists = db.raw.get(uuid=self.uuid)
        payload = json.dumps(self.document)

        if exists:
            return db.raw.update(uuid=self.uuid, payload=payload)

        new_doc = Raw(uuid=self.uuid, data=payload)
        return db.raw.add(payload=new_doc)
