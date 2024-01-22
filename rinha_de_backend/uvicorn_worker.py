from uvicorn.workers import UvicornWorker


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "uvloop",
                     "http": "h11",
                     "lifespan": "auto",
                     "limit_concurrency": 2048,
                     "limit_max_requests": 20000,
                     "backlog": 4096,
                     "access_log": False}
