FROM php:5.6-apache


# ope-wamap - Wamap.org - offline version of the website
# Build with docker build -t ope-wamap .

#INSTRUCTIONS
# Build the container and run it with the docker-compose command
# Import wamap classes, run resource import script


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="wamap.org offline website - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

RUN apt-get update \
	&& apt-get install -y \
		git \
		libfreetype6-dev \
		libjpeg62-turbo-dev \
		libmcrypt-dev \
		libpng12-dev \
		php5-mysql vim zlib1g-dev \
		mimetex \
	&& docker-php-ext-install -j$(nproc) iconv mcrypt mysqli pdo pdo_mysql zip  \
	&& docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ \
	&& a2enconf serve-cgi-bin \
	&& a2enmod cgi


RUN cd /var/www \
	&& git clone https://github.com/drlippman/IMathAS.git html \
	&& chown -R www-data:www-data html

#VOLUME ["/var/www/html"]
EXPOSE 80
