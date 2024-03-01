import os

from .wsgi import application


def _do_patch_psycopg2():
    _do_patch = bool(int(os.getenv("DB_USE_DB_GEVENTPOOL", "0")))
    if _do_patch:
        from psycogreen.gevent import patch_psycopg
        patch_psycopg()
        print(">>> Psycopg patched!")


def _has_gevent_patched():
    import gevent.socket
    import socket

    patched = socket.socket == gevent.socket.socket
    print(f">>> Gevent has Patched: {patched}")
    if not patched:
        import gevent.monkey
        print(">>> Gevent patching: ", end="")
        gevent.monkey.patch_all()
        print(socket.socket == gevent.socket.socket)


_has_gevent_patched()
_do_patch_psycopg2()
