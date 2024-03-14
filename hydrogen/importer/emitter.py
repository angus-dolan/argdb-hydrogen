from hydrogen import Database, ArgumentModel, Config
from hydrogen.search import Search
import redis
import json

db, search_engine, config = Database(), Search(), Config()

cache_host = config.get('redis', 'host')
cache_port = config.get('redis', 'port')
cache_db = config.get('redis', 'db')


class IEmitter:
    def __init__(self):
        pass

    def emit(self):
        pass


class RedisEmitter:
    def __init__(self, buffer, max_size_bytes=104857600, redis_host=cache_host, redis_port=cache_port, redis_db=cache_db):
        self.buffer = buffer
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.max_size_bytes = max_size_bytes  # 100MB

    def emit(self):
        self.redis_client.flushall()
        chunk_data = []
        current_chunk_size = 0
        list_key = "arguments_list"  # Key for the list that holds all chunk keys

        for src_id, argument in self.buffer.items():
            argument_json = json.dumps(argument) + "__NEWARGUMENT__"  # Add newline for readability
            argument_size = len(argument_json.encode('utf-8'))

            if current_chunk_size + argument_size > self.max_size_bytes:
                # Store the current chunk in Redis
                chunk_key = f"argument_chunk:{len(chunk_data)}"
                self.redis_client.set(chunk_key, ''.join(chunk_data))
                self.redis_client.rpush(list_key, chunk_key)

                # Reset for the next chunk
                chunk_data = [argument_json]
                current_chunk_size = argument_size
            else:
                chunk_data.append(argument_json)
                current_chunk_size += argument_size

        if chunk_data:
            chunk_key = f"argument_chunk:{len(chunk_data)}"
            self.redis_client.set(chunk_key, ''.join(chunk_data))
            self.redis_client.rpush(list_key, chunk_key)


class SqliteEmitter(IEmitter):
    def __init__(self, uuid=None, doc=None):
        super().__init__()
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
            return db.arguments.update(uuid=self.uuid, payload=db_payload)

        new_record = ArgumentModel(uuid=self.uuid, data=db_payload)
        db.arguments.add(payload=new_record)
