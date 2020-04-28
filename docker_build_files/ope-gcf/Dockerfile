FROM nginx

# ope-gcf - GCFLearnFree.org - offline version of the website
# Build with docker build -t ope-gcf .

#INSTRUCTIONS
# Build the container and run it with the docker-compose command
# Copy gcflearnfree.org files into volume folder


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="GCFLearnFree.org offline website - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

COPY start.sh /start.sh
RUN chmod +x /start.sh

VOLUME ["/usr/share/nginx/html"]
EXPOSE 80

ENTRYPOINT ["/start.sh"]


