FROM alpine:3.9.4
#FROM alpine:3.4

# Pulled from andyshinn/docker-dnsmasq
# ope-dns  - Open Prison Education dns device
# Build with docker build -t ope-dns .

# Run with
# docker run -p 53:53/tcp -p 53:53/udp --cap-add=NET_ADMIN andyshinn/dnsmasq:2.75 -A /consul/10.17.0.2. This will send a request for redis.service.consul to 10.17.0.2

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="DNS Server for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"
LABEL version=0.1


RUN apk --no-cache add dnsmasq
EXPOSE 53/tcp 53/udp
ENTRYPOINT ["dnsmasq", "-k", "--bind-dynamic", "--log-queries", "--log-facility=-"]
# "--bind-interfaces"
