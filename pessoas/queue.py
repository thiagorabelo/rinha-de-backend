import logging
import gevent

from django.conf import settings
from django.db import connection
from itertools import cycle
from gevent.queue import Queue, Empty


logger = logging.getLogger("rinha-de-backend")


# insert_task = Queue()

_query = """
insert into pessoas_pessoa ("id", "apelido", "nome", "nascimento", "stack")
values ( %(id)s, %(apelido)s, %(nome)s, %(nascimento)s, %(stack)s )
""".strip()


INSERT_BUFFER_SIZE = 200
QUEUE_GET_TIMEOUT = 1


class QueueCycle:
    def __init__(self, *queues):
        self._pool = cycle(queues)

    def get(self):
        return next(self._pool)


def init_workers(num_workers=0):
    num_workers = abs(num_workers or settings.NUM_INSERT_WORKERS)
    queues = tuple(Queue() for _ in range(num_workers))
    for q in queues:
        gevent.spawn(insert_worker, q)
    return QueueCycle(*queues)


# Solução inspirada (tá mais pra copiada) de https://github.com/iancambrea/rinha-python-sanic em:
# https://github.com/iancambrea/rinha-python-sanic/blob/9b41ac9ecb991017dd9631e35076f32c543f1524/app/main.py
def insert_worker(queue, buffer_size=INSERT_BUFFER_SIZE, queue_get_timeout=QUEUE_GET_TIMEOUT):
    while True:
        buffer = []

        while len(buffer) < buffer_size:
            try:
                pessoa_dict = queue.get(timeout=queue_get_timeout)
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
