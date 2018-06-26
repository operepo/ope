FROM postgres:9.6-alpine

# ope-postgresql - Postgresql server, used by other containers for the OPE project
# Build with docker build -t ope-postgresql .


LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Postgresql container used by canvas - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="0.4"


LABEL rebuild=14
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
COPY update_pw.sh /update_pw.sh
RUN chmod +x /update_pw.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
VOLUME /var/lib/postgresql/data
EXPOSE 5432
CMD ["postgres"]
