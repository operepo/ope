FROM debian:jessie
ENV DEBIAN_FRONTEND noninteractive

#
# ope-smc - Student Mangement Console - import/enrollment/videos offline image
# Build with docker build -t ope-smc .
#TODO - Finish - test  need winrm libs, need python-crypto (pycrypto), ffmpeg

#INSTRUCTIONS
# Build the smc container and run it with the docker-compose command
# View the smc website to set your admin password and configure Canvas/AD integration.

# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Student Management Console - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

# env vars

#TODO - change admin password!!!
# Should be passed by compose file to override defaults
ENV IT_PW changeme
ENV OFFICE_PW changeme
ENV INSTALL_DIR /home/www-data
ENV W2P_DIR $INSTALL_DIR/web2py
ENV CERT_PASS web2py
ENV TERM=xterm
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_RUN_DIR /var/run/apache2

WORKDIR $INSTALL_DIR


USER root

# Add backports repo so we can install ffmpeg
RUN echo 'deb http://ftp.debian.org/debian jessie-backports main' >> /etc/apt/sources.list

RUN mkdir $W2P_DIR
# /home/www-data/web2py

# update and install necessary packages
RUN apt-get update && \
	apt-get -y upgrade && \
	apt-get -y --no-install-recommends install ca-certificates nano gettext-base libxml2-dev python python-dev python-pip python-setuptools unzip wget net-tools git apache2-mpm-worker apache2-threaded-dev libapache2-mod-wsgi libapache2-mod-proxy-html ssl-cert unzip ffmpeg vim python-ldap python-crypto openssl python-mysqldb zip tar python-psycopg2 python-matplotlib python-reportlab   && \
	PIPPATH=`which pip` && \
	apt-get autoremove && \
	apt-get autoclean && \
	apt-get clean

# Install FFMPeg and related libraries
#RUN apt -t jessie-backports install ffmpeg libav-tools libavcodec-extra libavcodec-extra57 libavcodec57 libavdevice57 libavfilter6 libavformat57 libavresample3 libavutil55 libpostproc54 libswresample2 libswscale4 

# Lower mpm-prefork minimum servers
RUN sed -i "s/StartServers          5/StartServers          2/g" /etc/apache2/apache2.conf
RUN sed -i "s/MinSpareServers       5/MinSpareServers       2/g" /etc/apache2/apache2.conf
RUN sed -i "s/MaxSpareServers      10/MaxSpareServers       5/g" /etc/apache2/apache2.conf

LABEL rebuild=19
	



# Make a test cert
RUN openssl genrsa -passout pass:$CERT_PASS 2048 > /etc/ssl/private/web2py.key && \
	chmod 400 /etc/ssl/private/web2py.key && \
	openssl req -new -x509 -nodes -sha1 -days 1780 -subj "/C=US/ST=Washington/L=Port Angeles/O=OpenPrisonEducation/CN=smc.ed" -key /etc/ssl/private/web2py.key > /etc/ssl/certs/web2py.crt && \
	openssl x509 -noout -fingerprint -text < /etc/ssl/certs/web2py.crt > /etc/ssl/web2py.info



WORKDIR $W2P_DIR
RUN chown -R www-data:www-data $W2P_DIR
USER www-data

# get and install web2py
RUN wget http://web2py.com/examples/static/web2py_src.zip && \
    unzip -o web2py_src.zip -d .. && \
	rm web2py_src.zip && \	
	mv handlers/wsgihandler.py ./wsgihandler.py && \
	chown -R www-data:www-data .


RUN python -c "from gluon.main import save_password; save_password('$IT_PW',80)" && \
	python -c "from gluon.main import save_password; save_password('$IT_PW',443)"

LABEL rebuild=2
# Checkout release copy of SMC
RUN git clone https://github.com/frankyrumple/smc.git $W2P_DIR/applications/smc
RUN cp -f $W2P_DIR/applications/smc/routes.py $W2P_DIR/routes.py

# Add a first run file so that next time a page is hit db migration happens
# Not needed - code detects first run with cache.ram
# RUN touch $W2P_DIR/applications/smc/.first_run


USER root

RUN chown -R www-data:www-data $W2P_DIR

# Add shortcut to set_admin_password.py
RUN echo '#!/bin/sh\ncd /home/www-data/web2py/applications/smc\npython set_admin_password.py' > /bin/set_admin_password
RUN chmod +x /bin/set_admin_password
RUN chmod +x /home/www-data/web2py/applications/smc/set_admin_password.py

LABEL rebuild=24
# Take out default site
RUN rm -f /etc/apache2/sites-enabled/*
# Configure apache to run web2py app
COPY web2py.conf /etc/apache2/sites-available/web2py.conf
RUN ln -s ../sites-available/web2py.conf /etc/apache2/sites-enabled/
# Turn on apache modules
RUN ln -s /etc/apache2/mods-available/proxy_http.load            /etc/apache2/mods-enabled/proxy_http.load
RUN a2enmod ssl
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN a2enmod headers
RUN a2enmod expires
RUN a2enmod wsgi

VOLUME ["/home/www-data/web2py/applications/smc/cache", "/home/www-data/web2py/applications/smc/databases", "/home/www-data/web2py/applications/smc/errors", "/home/www-data/web2py/applications/smc/private", "/home/www-data/web2py/applications/smc/static/media", "/home/www-data/web2py/applications/smc/uploads"] 

EXPOSE 80 443
# 8000
ENV USER=www-data
#ENTRYPOINT python web2py.py
#CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
ENTRYPOINT bash -c '. /etc/apache2/envvars ; chown -R www-data:www-data /home/www-data ; rm -Rf /var/run/apache2/*; /usr/sbin/apache2 -D FOREGROUND'
