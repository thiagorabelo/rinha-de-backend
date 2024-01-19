import redis.asyncio as redis


# TODO: Completar esta classe (serializer, deserializer)
class SimpleCache:
    def __init__(self, host, port, db):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db)

    async def aset(self, key, value):
        client = redis.Redis(connection_pool=self.pool)
        return await client.set(key, value)

    async def aget(self, key):
        client = redis.Redis(connection_pool=self.pool)
        if value := await client.get(key):
            return value.decode('utf-8')
        return None
