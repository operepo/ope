FROM alpine
MAINTAINER You <you@example.com>
RUN apk update && \
    apk add util-linux && \
    rm -rf /var/cache/apk/*
ENTRYPOINT ["nsenter", "--target", "1", "--mount", "--uts", "--ipc", "--net", "--pid"]
