import asyncio
import codecs
import json
import types

from django.conf import settings

from .models import Pessoa


insert_queue = asyncio.Queue()


def init_pessoa_inserter_loop(loop):
    loop = asyncio.get_event_loop()
    loop.create_task(pessoas_inserter())


def get_body_as_json(request):
    """
    Adiciona o método request.json() ao objeto request
    """
    if not hasattr(request, '_json_cache'):
        if request.META.get('CONTENT_TYPE') == 'application/json':
            encoding = settings.DEFAULT_CHARSET
            stream = codecs.getreader(encoding)(request)
            request._json_cache = json.load(stream)
        else:
            request._json_cache = None
    return request._json_cache


async def pessoas_inserter():
    timeout = 0.2

    while True:
        try:
            pessoa = await asyncio.wait_for(
                insert_queue.get(),
                timeout=timeout
            )
            await pessoa.asave()
        except asyncio.TimeoutError:
            break
