FROM nginx

# ope-clamv - clam antivirus files - makes it easy for offline sync of antivirus file
# Build with docker build -t ope-clamav .
# Will automatically download AV files on first every startup if they are avialable

#INSTRUCTIONS
# Build the container and run it with the docker-compose command
# After it is done downloading virus files, use the standard sync tool to copy them into your offline network

# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="ClamAV offline virus patterns - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

RUN apt-get update && \
	apt-get -y install -y wget dos2unix supervisor curl

LABEL rebuild=3
ADD dl_virus_defs.sh /
RUN chmod +x /dl_virus_defs.sh && \
dos2unix /dl_virus_defs.sh

VOLUME ["/usr/share/nginx/html"]
EXPOSE 80
