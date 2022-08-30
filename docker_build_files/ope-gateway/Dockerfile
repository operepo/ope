#FROM nginx:1.11.3
#
FROM jwilder/nginx-proxy:alpine
LABEL rebuild=2

# ope-gateway  - Open Prison Education gateway device
# Build: Follow instructions at https://github.com/operepo/ope

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Web Gateway for Open Prison Education - source files at https://github.com/operepo"
LABEL vendor="openprisoneducation.com"
LABEL version="0.8"

ARG VERSION=dev

RUN apk add nano


LABEL rebuild=138
# public_certs moved under /usr/share/nginx/html
# Make public_certs folder so we can make it easy to grab crt file
#RUN mkdir -p /public_certs \
#    && chmod 755 /public_certs \
#    && mkdir -p /app
	
COPY docker-entrypoint.sh /app/
COPY init_certs.sh /app/
COPY openssl.cnf.tmpl /app/
COPY nginx.tmpl /app/
#COPY forego /app/
#COPY Procfile /app/
# *** NOTE -  conf.d is mounted, so need to copy over files on startup in the init_certs script
COPY uploads.conf /app/
COPY gateway.conf /app/
COPY nginx.conf /app/nginx.conf
COPY proxy.conf /app/
#COPY fogserver.conf /etc/nginx/conf.d/
# /etc/nginx/conf.d/uploads.conf
COPY index.html /app/
COPY 502.html /app/
WORKDIR /app/
RUN chmod +x /app/*.sh

# Update - do NOT wan't to mount individual files, mount folder instead
#ENV DOCKER_HOST unix:///tmp/docker.sock
ENV DOCKER_HOST unix:///var/run/docker.sock

VOLUME ["/etc/nginx/certs", "/tmp/docker.sock", "/etc/nginx/vhost.d", "/usr/share/nginx/html", "/etc/nginx/dhparam", "/etc/nginx/conf.d" ]

EXPOSE 80 443

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["forego", "start", "-r"]




