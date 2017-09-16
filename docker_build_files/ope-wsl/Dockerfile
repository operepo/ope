FROM mediawiki:stable

# ope-wsl - Offline version of Washington State Library resource wiki
# Build with docker build -t ope-wsl .

#INSTRUCTIONS
# Build the container and run it with the docker-compose command
# Sync offline copies of website content into volume


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Washington State Library offline resource wiki - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

# Copy in our settings
COPY LocalSettings.php /var/www/html/LocalSettings.php

# Copy in our custom startup script
# TOOD

VOLUME ["/var/www/html/sites"]
EXPOSE 80
