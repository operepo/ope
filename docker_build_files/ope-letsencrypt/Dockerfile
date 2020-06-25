FROM jrcs/letsencrypt-nginx-proxy-companion:stable

# ope-letsencrypt  - Open Prison Education auto ssl app (only works online)
# Build: Follow instructions at https://github.com/frankyrumple/ope

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="SSL/Letsencrypt app for Open Prison Education - source files at https://github.com/operepo"
LABEL vendor="openprisoneducation.com"
LABEL version="0.6"






ENTRYPOINT [ "/bin/bash", "/app/entrypoint.sh" ]
CMD [ "/bin/bash", "/app/start.sh" ]

