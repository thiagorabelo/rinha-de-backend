#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-error}"

exec gunicorn \
    "rinha_de_backend.asgi:application" \
    --worker-class "uvicorn.workers.UvicornWorker" \
    --name "Rinha de Backend - Python" \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --log-level "${LOG_LEVEL}" \
    --log-file -
