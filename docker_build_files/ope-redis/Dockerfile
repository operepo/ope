FROM redis:8.10.3-alpine

# ope-redis - Redis server, used by other containers
# Build with docker build -t ope-redis .

#INSTRUCTIONS
# Build the container - shouldn't need any other setup other than linking containers to it

# To copy to offline server use the setup tool

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL Description="Redis container used by canvas - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.2"

LABEL version="4"

# Redis 8 images bundle extra modules (search, json, timeseries, bloom) that the entrypoint loads automatically.
# Canvas only uses core redis as a cache - drop them to save memory.
RUN rm -f /usr/local/lib/redis/modules/*.so

COPY redis.conf.tmpl /etc/redis.conf.tmpl
COPY start.sh /start.sh
RUN chmod +x /start.sh

VOLUME ["/data"]

#CMD ["redis-server", "/etc/redis.conf"]
CMD ["/start.sh"]
