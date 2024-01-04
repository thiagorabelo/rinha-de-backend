#!/bin/bash

WORKERS="$(expr "$(nproc --all)" \* 2 + 1)"  # 2N+1

exec gunicorn \
    "rinha_de_backend_python.wsgi:application" \
    --name "Rinha de Backend - Python" \
    --bind "0.0.0.0:8000" \
    --workers "${WORKERS}" \
    --threads 2 \
    --log-level error \
    --log-file -
