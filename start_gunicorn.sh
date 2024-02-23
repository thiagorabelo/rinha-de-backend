#!/bin/sh

BACKLOG="${BACKLOG:-2048}"
WORKER_CLASS="${WORKER_CLASS:-sync}"
# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
WORKER_CONNECTIONS="${WORKER_CONNECTIONS:-1000}"
THREADS="${THREADS:-2}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"

echo "O LOG_LEVEL é $LOG_LEVEL"

if [[ "${MIGRATE}" == "1" ]]; then
    sleep 1 && python manage.py migrate
fi

exec gunicorn \
    "rinha_de_backend.wsgi:application" \
    --backlog "${BACKLOG}" \
    --worker-class "${WORKER_CLASS}" \
    --workers "${WORKERS}" \
    --worker-connections "${WORKER_CONNECTIONS}" \
    --threads "${THREADS}" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --log-level "${LOG_LEVEL}" \
    --log-file "-"
