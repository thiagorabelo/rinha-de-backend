import pickle
import redis


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

    def has_key(self, key):
        client = redis.Redis(connection_pool=self.pool)
        return client.exists(key)

    def set(self, key, value):
        client = redis.Redis(connection_pool=self.pool)
        return client.set(key, value)

    def get(self, key):
        client = redis.Redis(connection_pool=self.pool)
        if value := client.get(key):
            return pickle.loads(value)
        return None

    def set_many(self, d):
        client = redis.Redis(connection_pool=self.pool)
        pipe = client.pipeline()
        for k, v in d.items():
            pipe.set(k, pickle.dumps(v))
        return pipe.execute()
