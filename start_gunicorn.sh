#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"


exec gunicorn \
    "rinha_de_backend.wsgi:application" \
    --worker-class 'gevent' \
    --workers "${WORKERS}" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --log-level "${LOG_LEVEL}" \
    --log-file -
