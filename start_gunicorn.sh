#!/bin/sh

# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
THREADS="${THREADS:-2}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"
WORKER_CLASS="${WORKER_CLASS:-sync}"

echo "O LOG_LEVEL é $LOG_LEVEL"

if [[ "${MIGRATE}" == "1" ]]; then
    sleep 1 && python manage.py migrate
fi

exec gunicorn \
    "rinha_de_backend.wsgi:application" \
    --worker-class "${WORKER_CLASS}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --log-level "${LOG_LEVEL}" \
    --log-file "-"
