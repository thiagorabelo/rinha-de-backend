#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"


exec gunicorn \
    "rinha_de_backend.asgi:application" \
    --worker-class "rinha_de_backend.uvicorn_worker.CustomUvicornWorker" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --workers "${WORKERS}" \
    --log-level "${LOG_LEVEL}" \
    --log-file -
