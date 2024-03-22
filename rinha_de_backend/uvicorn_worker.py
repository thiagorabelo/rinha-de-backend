import os

from uvicorn.workers import UvicornWorker


class CustomUvicornWorker(UvicornWorker):
    # TODO: REVER ESSES VALORES
    CONFIG_KWARGS = {"loop": "uvloop",
                     "http": "h11",
                     "lifespan": "auto",
                     "limit_concurrency": int(os.getenv("WORKER_CONNECTIONS", "4096")),
                     "limit_max_requests": int(os.getenv("MAX_REQUESTS", "100000")),
                     "backlog": int(os.getenv("BACKLOG", "10240")),
                     "access_log": bool(int(os.getenv("ACCESS_LO", "0")))}
