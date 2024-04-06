from hydrogen import Database, ArgumentModel, Config
import redis
import json

db, config = Database(), Config()

cache_host = config.get('redis', 'host')
cache_port = config.get('redis', 'port')
cache_db = config.get('redis', 'db')


class IEmitter:
    def __init__(self):
        pass

    def emit(self):
        pass


class RedisEmitter:
    def __init__(self, buffer, elastic_bytes_limit=31457280, redis_host=cache_host, redis_port=cache_port, redis_db=cache_db):
        """
        Elastic's bulk insert limit is 100mb
        In the engine, both a summary and embedding is added to the batch's payload
        Therefore batches are set to 30MB to accommodate this
        e.g. 30MB data payload + ~30MB summary + ~30MB embedding < 100MB
        """
        self.buffer = buffer
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.max_size_bytes = elastic_bytes_limit

    def store_chunk(self, chunk_data, chunk_key):
        """Store the chunk data in Redis as a set and add the chunk key to the list."""
        for data in chunk_data:
            self.redis_client.sadd(chunk_key, data)
        self.redis_client.rpush("chunk_list", chunk_key)

    def reset_chunk(self):
        """Reset chunk data and size for the next chunk."""
        return [], 0  # Returns a new empty chunk_data list and size

    def emit(self):
        self.redis_client.flushall()
        chunk_data, current_chunk_size = self.reset_chunk()
        chunk_index = 1

        for src_id, argument in self.buffer.items():
            argument_json = json.dumps(argument)
            argument_size = len(argument_json.encode('utf-8'))

            # Check if adding this argument would exceed max chunk size or if it's the first item
            if current_chunk_size + argument_size > self.max_size_bytes or not chunk_data:
                if chunk_data:
                    # Store the chunk
                    chunk_key = f"chunk:{chunk_index}"
                    self.store_chunk(chunk_data, chunk_key)
                    chunk_index += 1
                    chunk_data, current_chunk_size = self.reset_chunk()

            chunk_data.append(argument_json)
            current_chunk_size += argument_size

        # Store any remaining chunk data
        if chunk_data:
            chunk_key = f"chunk:{chunk_index}"
            self.store_chunk(chunk_data, chunk_key)


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
