import random

from django.utils.crypto import get_random_string as grs

from rinha_de_backend.redis_cache import SimpleCache as Cache


RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"


def get_random_string(length):
    return grs(length, RANDOM_STRING_CHARS)


async def cache_set(cache, keys):
    key = get_random_string(10)
    val = get_random_string(15)
    keys.append(key)
    await cache.aset(key, val)


async def cache_get(cache, keys):
    key = random.choice(keys)
    return await cache.aget(key)


def medir_tempo(loop, async_fn, *args, **kwargs):
    return loop.run_until_complete(async_fn(*args, **kwargs))


setup = """
import django
import os
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rinha_de_backend.settings')
django.setup()

from profiles import cache_set, cache_get, medir_tempo

loop = asyncio.new_event_loop()
"""

# Django Cache Framework
setup += """
from django.core.cache import cache
"""

# Custom Cache Schema
# setup += """
# from profiles import Cache
# cache =  Cache("localhost", 6379, 0)
# """

# from profiles import setup; import timeit; saida = []
# timeit.timeit('medir_tempo(loop, cache_set, cache, saida)', setup=setup, number=2000, globals={"saida": saida})
