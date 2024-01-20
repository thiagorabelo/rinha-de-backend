ARG PG_TAG=16.0-alpine

FROM postgres:${PG_TAG} as extension_builder

RUN mkdir -p /build

WORKDIR /build

RUN apk add --virtual .build-extension-deps build-base clang15 llvm15-dev \
    && wget -c https://github.com/EnterpriseDB/system_stats/archive/refs/tags/v2.1.tar.gz \
    && tar -xvzf v2.1.tar.gz \
    && cd system_stats-2.1 \
    && make USE_PGXS=1 \
    && make install USE_PGXS=1 \
    && cd .. \
    && rm -fr system_stats-2.1/ v2.1.tar.gz \
    && apk del .build-extension-deps


# FROM postgres:${PG_TAG}

# COPY --from=extension_builder /usr/local /usr