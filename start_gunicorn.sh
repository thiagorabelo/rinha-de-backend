#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
THREADS="${THREADS:-2}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"

echo "O LOG_LEVEL é $LOG_LEVEL"


exec gunicorn \
    "rinha_de_backend.wsgi:application" \
    --worker-class 'gevent' \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --log-level "${LOG_LEVEL}" \
    --log-file "-"
