from hydrogen import Database, ArgumentModel
from hydrogen.search import SearchEngine
import json

db, search_engine = Database(), SearchEngine()

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
        db_payload = json.dumps(self.document)

        if exists:
            db.arguments.update(uuid=self.uuid, payload=db_payload)
            # TODO: Update an existing search index
            return

        new_record = ArgumentModel(uuid=self.uuid, data=db_payload)
        db.arguments.add(payload=new_record)
        search_engine.add_document(self.uuid, self.document)
