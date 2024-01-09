#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-error}"

exec gunicorn \
    "rinha_de_backend.wsgi:application" \
    --name "Rinha de Backend - Python" \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --threads 2 \
    --log-level "${LOG_LEVEL}" \
    --log-file -
