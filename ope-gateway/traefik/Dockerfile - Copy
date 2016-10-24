FROM alpine:latest 
# 3.3
# ope-gateway  - Open Prison Education gateway device
# Build with docker build -t ope-gateway .

ARG VERSION=dev

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Web Gateway for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"
LABEL version=0.3

ADD start_traefik.sh /start_traefik.sh
RUN chmod +x /start_traefik.sh

RUN apk update \
  && apk --no-cache --no-progress add ca-certificates wget openssl \
  && update-ca-certificates \
  #&& wget https://github.com/emilevauge/traefik/releases/download/$VERSION/traefik \
  && wget -O /traefik  https://github.com/containous/traefik-library-image/raw/9d877ca7171211aabc2955ab1a301a685f6852fe/traefik \
  && chmod +x traefik \
  && mkdir /certs

# Uncomment these if you want to import your own certs from the ope/ope-gateway directory
#ADD cert.pem /certs/cert.pem
#ADD key.pem /certs/key.pem 
  
RUN if [ -e /certs/cert.pem ]; then echo "certs exist"; else openssl req -newkey rsa:4096 -x509 -nodes -days 1780 -subj "/C=US/ST=Washington/L=Port Angeles/O=OpenPrisonEducation/CN=gateway.ed" -keyout /certs/key.pem -out /certs/cert.pem; fi


EXPOSE 80 443 8080
# /certs folder can be mapped if you put your certs in the volumes directory
#VOLUME ["/certs"]
#ENTRYPOINT ["/start_traefik.sh"]
ENTRYPOINT ["/traefik"]
#CMD ["--help"]

