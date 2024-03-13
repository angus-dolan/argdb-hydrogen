from hydrogen import Database, ArgumentModel
from hydrogen.search import Search
import json

db, search_engine = Database(), Search()

class Emitter:
    def __init__(self, uuid=None, doc=None):
        self.document = doc
        self.uuid = uuid

    def set_uuid(self, uuid):
        self.uuid = uuid

    def set_document(self, doc):
        self.document = doc

    def emit(self):
        # print(search_engine.transform_sadface(self.document))
        # exists = db.arguments.get(uuid=self.uuid)
        # db_payload = json.dumps(self.document)
        #
        # if exists:
        #     return db.arguments.update(uuid=self.uuid, payload=db_payload)
        #
        # new_record = ArgumentModel(uuid=self.uuid, data=db_payload)
        # db.arguments.add(payload=new_record)
        search_engine.insert_document(self.document)
