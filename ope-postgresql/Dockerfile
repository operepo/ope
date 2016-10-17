FROM debian:jessie  ?? Better for postgresql?

# ope-postgresql - Postgresql server, used by other containers
# Build with docker build -t ope-postgresql .
TODO - Finish - postgresql, setup as a linked container for canvas
#INSTRUCTIONS
# Build the container 
# Set admin and canvas passwords




TODO - add user huskers ???

# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Postgresql container used by canvas - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"


RUN apt-get update

# Install dependencies
TODO
RUN apt-get install -y wget git python python-pkg-resources ucf net-tools

RUN mkdir /home/huskers/www????



VOLUME ["/var/log/redis", "/var/lib/redis"] TODO
EXPOSE 6379 ???
ENV USER=huskers ???
#ENTRYPOINT exec bash
ENTRYPOINT TODO - launch postgresql
