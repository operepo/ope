#FROM nginx:1.11.3
FROM jwilder/nginx-proxy:alpine

# ope-gateway  - Open Prison Education gateway device
# Build: Follow instructions at https://github.com/frankyrumple/ope

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Web Gateway for Open Prison Education - source files at https://github.com/operepo"
LABEL vendor="openprisoneducation.com"
LABEL version="0.6"

ARG VERSION=dev

LABEL rebuild=73
# public_certs moved under /usr/share/nginx/html
# Make public_certs folder so we can make it easy to grab crt file
#RUN mkdir -p /public_certs \
#    && chmod 755 /public_certs \
#    && mkdir -p /app
	
#COPY fogserver.conf /etc/nginx/conf.d/
COPY docker-entrypoint.sh /app/
COPY init_certs.sh /app/
COPY openssl.cnf.tmpl /app/
COPY nginx.tmpl /app/
#COPY forego /app/
#COPY Procfile /app/
COPY uploads.conf /app/
COPY gateway.conf /app/
# conf.d is mounted, so need to copy over files on startup
# /etc/nginx/conf.d/uploads.conf
COPY index.html /app/
WORKDIR /app/
RUN chmod +x /app/*.sh

# Update - do NOT wan't to mount individual files, mount folder instead
#ENV DOCKER_HOST unix:///tmp/docker.sock
ENV DOCKER_HOST unix:///var/run/docker.sock

VOLUME ["/etc/nginx/certs", "/tmp/docker.sock", "/etc/nginx/vhost.d", "/usr/share/nginx/html", "/etc/nginx/dhparam", "/etc/nginx/conf.d" ]

EXPOSE 80 443

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["forego", "start", "-r"]




