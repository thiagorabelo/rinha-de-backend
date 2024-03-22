import asyncio
import json

from asgiref.sync import sync_to_async
from concurrent.futures import ThreadPoolExecutor
from django.http import HttpRequest
from django.db import connection
from functools import wraps
from typing import Any


from .models import Pessoa


insert_queue = asyncio.Queue()


class BulkInsertBuffer:
    _query = """
    insert into pessoas_pessoa ("id", "apelido", "nome", "nascimento", "stack")
    values ( %(id)s, %(apelido)s, %(nome)s, %(nascimento)s, %(stack)s )
    """.strip()

    def __init__(self, max_size, timeout, loop=None):
        self.max_size = max_size
        self.timeout = timeout
        self._loop = loop
        self.buffer = []
        self.task = None

    @property
    def loop(self):
        if self._loop:
            return self._loop
        return asyncio.get_event_loop()

    def _transforma(self, pessoa):
        return {
            "id": pessoa.id,
            "apelido": pessoa.apelido,
            "nome": pessoa.nome,
            "nascimento": pessoa.nascimento,
            "stack": pessoa.stack,
        }

    def adicionar_pessoa(self, pessoa):
        self.buffer.append(self._transforma(pessoa))

        if len(self.buffer) >= self.max_size:
            self.bulk_insert()

        if self.task:
            self.task.cancel()

        self.task = asyncio.ensure_future(self.schedule_insert(), loop=self.loop)

    async def schedule_insert(self):
        await asyncio.sleep(self.timeout)
        await self.abulk_insert()

    def bulk_insert(self):
        if self.buffer:
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(self._connect_db)
                executor.shutdown()

    async def abulk_insert(self):
        if self.buffer:
            await sync_to_async(self._connect_db)()

    def _connect_db(self):
        try:
            with connection.cursor() as cursor:
                print(f"Inserindo {len(self.buffer)} registros")
                cursor.executemany(self._query, self.buffer)
        except Exception as ex:
            print(f">>> {str(ex)}")
        finally:
            self.buffer = []
            if self.task:
                self.task.cancel()


def get_body_as_json(request: HttpRequest) -> dict[str, Any] | None:
    """
    Converte o corpo da requisição do formato JSON para um dicionário
    """
    if not hasattr(request, "_json_cache"):
        if request.META.get("CONTENT_TYPE") == "application/json":
            request._json_cache = json.loads(request.read())
        else:
            request._json_cache = None
    return request._json_cache
