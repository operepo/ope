FROM debian:jessie
# ope-kalite - KALite - Khan Academy offline image
# Build with docker build -t ope-kalite .

#INSTRUCTIONS
# Build the kalite container and run it with the docker-compose command
# View the kalite website and create your admin user.
# Download all videos

# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="KALite Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"


RUN apt-get update

RUN apt-get install -y wget

# Get the kalite install file
RUN wget -q -O kalite.deb https://learningequality.org/r/deb-bundle-installer-0-16

# Install dependencies
RUN apt-get install -y python python-pkg-resources ucf net-tools

# Install it
RUN dpkg -i kalite.deb

RUN rm kalite.deb
RUN apt-get clean

VOLUME ["/root/.kalite"]
EXPOSE 8008
ENV USER=ka-lite
#ENTRYPOINT exec bash
ENTRYPOINT exec kalite start --foreground
