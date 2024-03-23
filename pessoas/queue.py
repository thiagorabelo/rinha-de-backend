import logging

from django.db import connection
from gevent.queue import Queue, Empty


logger = logging.getLogger("rinha-de-backend")


insert_task = Queue()

_query = """
insert into pessoas_pessoa ("id", "apelido", "nome", "nascimento", "stack")
values ( %(id)s, %(apelido)s, %(nome)s, %(nascimento)s, %(stack)s )
""".strip()


INSERT_BUFFER_SIZE = 200
QUEUE_GET_TIMEOUT = 1


# Solução inspirada (tá mais pra copiada) de https://github.com/iancambrea/rinha-python-sanic em:
# https://github.com/iancambrea/rinha-python-sanic/blob/9b41ac9ecb991017dd9631e35076f32c543f1524/app/main.py
def insert_worker(buffer_size=INSERT_BUFFER_SIZE, queue_get_timeout=QUEUE_GET_TIMEOUT):
    while True:
        buffer = []

        while len(buffer) < buffer_size:
            try:
                pessoa_dict = insert_task.get(timeout=queue_get_timeout)
                if pessoa_dict:
                    buffer.append(pessoa_dict)
            except Empty:
                break

        if buffer:
            insert_into_db(buffer)


def insert_into_db(buffer):
    try:
        with connection.cursor() as cursor_wrapper:
            cursor = cursor_wrapper.cursor
            # logger.debug("Inserindo %d pessoas", len(buffer))
            cursor.executemany(_query, buffer)
    except Exception as ex:
        logger.error("Houve um Erro: [%s]", str(ex))
