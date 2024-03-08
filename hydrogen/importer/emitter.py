from database import Database, Arguments
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
        exists = db.arguments.get(uuid=self.uuid)
        payload = json.dumps(self.document)

        if exists:
            return db.arguments.update(uuid=self.uuid, payload=payload)

        new_doc = Arguments(uuid=self.uuid, data=payload)
        return db.arguments.add(payload=new_doc)
