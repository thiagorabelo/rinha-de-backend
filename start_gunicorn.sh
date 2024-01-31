#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"


# --worker-class 'gevent'  # Por algum motivo 'settings.DATABASES["default"]["CONN_MAX_AGE"]' deixa de funcionar
exec gunicorn \
    "rinha_de_backend.wsgi:application" \
    --worker-class 'sync' \
    --workers "${WORKERS}" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --log-level "${LOG_LEVEL}" \
    --log-file -
