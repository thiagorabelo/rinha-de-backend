from django.core.cache import cache
# from rinha_de_backend.redis_cache import cache

from .models import Pessoa


def _pessoa_id_key(id):
    return f"pessoa:{id}"


def _pessoa_apelido_key(apelido):
    return f"pessoa:apelido:{apelido}"


def get_pessoa_dict_by_cache_or_db(pk):
    if pessoa_dict := cache.get(_pessoa_id_key(pk)):
        return pessoa_dict
    pessoa_dict = Pessoa.get_as_dict(pk=pk)
    set_pessoa_dict_cache(pk, pessoa_dict)
    return pessoa_dict


def has_pessoa_apelido_cached(pessoa):
    return cache.has_key(_pessoa_apelido_key(pessoa.apelido))


def set_pessoa_dict_cache(pk, pessoa_dict):
    return cache.set_many({
        _pessoa_id_key(pk): pessoa_dict,
        _pessoa_apelido_key(pessoa_dict["apelido"]): "1"
    })
