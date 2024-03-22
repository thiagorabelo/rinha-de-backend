
# from django.core.cache import cache

import os

from rinha_de_backend.redis_cache import SimpleCache
from .models import Pessoa


cache = SimpleCache(url=os.environ["CACHE_LOCATION"])


def _pessoa_id_key(id):
    return f"pessoa:{id}"


def _pessoa_apelido_key(apelido):
    return f"pessoa:apelido:{apelido}"


async def get_pessoa_dict_by_cache_or_db(pk):
    if pessoa_dict := await cache.aget(_pessoa_id_key(pk)):
        return pessoa_dict
    pessoa_dict = await Pessoa.aget_as_dict(pk=pk)
    await set_pessoa_dict_cache(pk, pessoa_dict)
    return pessoa_dict


async def has_pessoa_apelido_cached(pessoa):
    return await cache.ahas_key(_pessoa_apelido_key(pessoa.apelido))


async def set_pessoa_dict_cache(pk, pessoa_dict):
    return await cache.aset_many({
        _pessoa_id_key(pk): pessoa_dict,
        _pessoa_apelido_key(pessoa_dict["apelido"]): "1"
    })
