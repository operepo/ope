FROM alpine:3.9.4

# Pulled from cturra/docker-ntp
# ope-ntp  - Open Prison Education ntp device
# Build with docker build -t ope-ntp .


MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="NTP Server for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"
LABEL version=0.1


RUN apk --no-cache add chrony

COPY startup.sh /opt/startup.sh

EXPOSE 123/udp

HEALTHCHECK cmd chronyc tracking || exit 1

ENTRYPOINT [ "/bin/sh", "/opt/startup.sh" ]
