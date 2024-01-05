#!/bin/bash

WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1

exec gunicorn \
    "rinha_de_backend_python.asgi:application" \
    --worker-class "uvicorn.workers.UvicornWorker" \
    --name "Rinha de Backend - Python" \
    --bind "0.0.0.0:8000" \
    --workers "${WORKERS}" \
    --log-level error \
    --log-file -
