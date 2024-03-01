ARG PYTHON_TAG=3.12.1-alpine

FROM python:${PYTHON_TAG}

RUN addgroup galo && adduser -S -G galo -g "App Runner" galo \
    && mkdir -p /app \
    && chown galo:galo -R /app \
    && apk add build-base linux-headers

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY --chown=galo:galo . /app

WORKDIR /app

USER galo

CMD /app/start_uwsgi.sh
