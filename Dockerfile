ARG PYTHON_TAG=3.12.1-alpine

FROM python:${PYTHON_TAG}

RUN addgroup galo && adduser -S -G galo -g "App Runner" galo \
    && mkdir -p /app \
    && chown galo:galo -R /app

COPY --chown=galo:galo . /app

WORKDIR /app

RUN pip install -r requirements.txt

USER galo

CMD ./manage.py migrate && /app/start_uvicorn.sh
