#!/bin/sh

BACKLOG="${BACKLOG:-2048}"
WORKERS="${WORKERS:-2}"
WORKER_CONNECTIONS="${WORKER_CONNECTIONS:-1000}"
BIND_UWSGI="${BIND:-/tmp/socks/$(hostname).sock}"
BIND_HTTP="${BIND_HTTP}"

if [ -z "${BIND_HTTP}" ]; then
    BIND="--socket ${BIND_UWSGI}"
    BIND_EXTRA="--chmod-socket=666"
else
    BIND="--http-socket ${BIND_HTTP}"
    BIND_EXTRA=""
fi

if [[ "${MIGRATE}" == "1" ]]; then
    sleep 1 && python manage.py migrate
fi

exec uwsgi \
    --module "rinha_de_backend.wsgi_patched:application" \
    ${BIND} ${BIND_EXTRA} \
    --master \
    --single-interpreter \
    --listen "${BACKLOG}" \
    --workers "${WORKERS}" \
    --gevent "${WORKER_CONNECTIONS}" \
    --gevent-monkey-patch \
    --gevent-early-monkey-patch \
    --procname-prefix "Rinha de Backend | " \
    --disable-logging \
    --die-on-term
