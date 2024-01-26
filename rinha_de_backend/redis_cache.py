import pickle
import redis.asyncio as redis

from django.conf import settings


def _create_pool_factory(host=None, port=None, db=None, url=None):
    if url:
        return lambda: redis.ConnectionPool.from_url(url)
    return lambda: redis.ConnectionPool(host=host, port=port, db=db)


# TODO: Completar esta classe (serializer, deserializer)
class SimpleCache:
    def __init__(self, host=None, port=None, db=None, url=None):
        self._pool_factory = _create_pool_factory(host=host, port=port, db=db, url=url)
        self._pool = None

    @property
    def pool(self):
        if not self._pool:
            self._pool = self._pool_factory()
        return self._pool

    async def ahas_key(self, key):
        client = redis.Redis(connection_pool=self.pool)
        return await client.exists(key)

    async def aset(self, key, value):
        client = redis.Redis(connection_pool=self.pool)
        return await client.set(key, value)

    async def aget(self, key):
        client = redis.Redis(connection_pool=self.pool)
        if value := await client.get(key):
            return pickle.loads(value)
        return None

    async def aset_many(self, d):
        client = redis.Redis(connection_pool=self.pool)
        pipe = client.pipeline()
        for k, v in d.items():
            pipe.set(k, pickle.dumps(v))
        return await pipe.execute()


cache = SimpleCache(url=settings.CACHES["default"]["LOCATION"])
