FROM debian:jessie
# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .
TODO - Finish - Canvas install, ruby gems, link to redis, postgresql 
#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.

TODO - add user huskers

# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Canvas LMS by Instructure - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"


RUN apt-get update

# Install dependencies
TODO
RUN apt-get install -y wget git python python-pkg-resources ucf net-tools

RUN mkdir /home/huskers/canvas

# Checkout current copy of canvas
RUN git ....

# Install canvas deps


VOLUME ["/home/huskers/canvas/tmp", "/home/huskers/canvas/config", "/home/huskers/canvas/log"]
EXPOSE 80 443
ENV USER=smcuser
#ENTRYPOINT exec bash
ENTRYPOINT TODO - canvas start? - and start background runner
