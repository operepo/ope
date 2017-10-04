FROM nginx:alpine

# ope-git - OPE Git Server - offline version
# Build with docker build -t ope-git .

#INSTRUCTIONS
# Build the container and run it with the docker-compose command


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Offline Git Server - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

COPY nginx.conf /etc/nginx/nginx.conf

VOLUME ["/usr/share/nginx/html"]
EXPOSE 80
