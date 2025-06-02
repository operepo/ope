FROM debian:stretch

# ope-router - Router config for OPE project - includes multicast and kernel modules 
# Build with docker build -t ope-router .

#INSTRUCTIONS
# Build the container and run it with the docker-compose command


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Routing and multicast support in ope-fog - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

RUN apt-get update; apt-get install -y pimd iptables dos2unix kmod igmpproxy nano pimd

LABEL rebuild=4

COPY start.sh /start.sh
COPY igmpproxy.conf /etc/igmpproxy.conf
RUN chmod +x /start.sh; dos2unix /start.sh; dos2unix /etc/igmpproxy.conf

#VOLUME ["/usr/share/nginx/html"]
#EXPOSE 80

ENTRYPOINT exec /start.sh

