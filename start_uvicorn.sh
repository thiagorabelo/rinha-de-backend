#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"

# uvicorn --port 9999 --workers 4 --loop uvloop --limit-concurrency 1000 --backlog 500 --limit-max-requests 2000 "rinha_de_backend.asgi:application"

exec gunicorn \
    "rinha_de_backend.asgi:application" \
    --worker-class "uvicorn.workers.UvicornWorker" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --workers "${WORKERS}" \
    --log-level "${LOG_LEVEL}" \
    --log-file -
