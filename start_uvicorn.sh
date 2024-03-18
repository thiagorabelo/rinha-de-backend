#!/bin/sh


# "loop": "uvloop",
# "http": "h11",
# "lifespan": "auto",
# "limit_concurrency": 2048,
# "limit_max_requests": 20000,
# "backlog": 4096,
# "access_log": False

BACKLOG="${BACKLOG:-2048}"
# WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1
WORKERS="${WORKERS:-4}"
BIND="${BIND:-unix:/tmp/socks/$(hostname).sock}"
LOG_LEVEL="${LOG_LEVEL:-error}"

echo "O LOG_LEVEL é $LOG_LEVEL"

if [[ "${MIGRATE}" == "1" ]]; then
    sleep 1 && python manage.py migrate
fi

exec gunicorn \
    "rinha_de_backend.asgi:application" \
    --worker-class "rinha_de_backend.uvicorn_worker.CustomUvicornWorker" \
    --name "Rinha de Backend - Python" \
    --bind "${BIND}" \
    --workers "${WORKERS}" \
    --log-level "${LOG_LEVEL}" \
    --log-file -
