#!/bin/sh


BACKLOG="${BACKLOG:-2048}"
# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
WORKER_CONNECTIONS="${WORKER_CONNECTIONS:-2048}"
BIND="${BIND:-/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"

echo "O LOG_LEVEL é $LOG_LEVEL"

if [[ "${MIGRATE}" == "1" ]]; then
    sleep 1 && python manage.py migrate
fi

rm -f "${BIND}"

set -x
exec uvicorn \
    --uds "${BIND}" \
    --loop "uvloop" \
    --http httptools \
    --backlog "${BACKLOG}" \
    --workers "${WORKERS}" \
    --limit-concurrency "${WORKER_CONNECTIONS}" \
    --lifespan off \
    --no-access-log \
    --log-level "${LOG_LEVEL}" \
    --proxy-headers \
    "rinha_de_backend.asgi:application"
