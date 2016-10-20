FROM ubuntu:16.10
#FROM ubuntu:trusty
# Original build from thehipbot/docker-web2py
#
# ope-smc - Student Mangement Console - import/enrollment/videos offline image
# Build with docker build -t ope-smc .
#TODO - Finish - test  need winrm libs, need python-crypto (pycrypto), 
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

WORKDIR $INSTALL_DIR

USER root

# update ubuntu and install necessary packages
RUN apt-get update && \
	apt-get autoremove && \
	apt-get autoclean && \
	apt-get -y install nginx-full ca-certificates nginx nano gettext-base build-essential python-dev libxml2-dev python-pip unzip wget supervisor ucf net-tools git uwsgi unzip && \
	pip install setuptools --no-use-wheel --upgrade && \	
	PIPPATH=`which pip` && \
	$PIPPATH install --upgrade uwsgi && \
	apt-get clean && \
	mkdir /etc/nginx/conf.d/web2py

RUN mkdir /home/www-data/web2py

# Install smc specific packages
RUN apt-get -y install python-ldap python-crypto
	#PIPPATH=`which pip` && \
	#$PIPPATH install pycrypto
	#$PIPPATH install python-ldap && \
	
LABEL rebuild=14

# copy nginx config files from repo
ADD gzip_static.conf /etc/nginx/conf.d/web2py/gzip_static.conf
ADD gzip.conf /etc/nginx/conf.d/web2py/gzip.conf
ADD web2py /etc/nginx/sites-available/web2py

# setup nginx
RUN ln -s /etc/nginx/sites-available/web2py /etc/nginx/sites-enabled/web2py && \
	rm /etc/nginx/sites-enabled/default && \
	mkdir /etc/nginx/ssl && cd /etc/nginx/ssl && \
	openssl genrsa -passout pass:$CERT_PASS 1024 > web2py.key && \
	chmod 400 web2py.key && \
	openssl req -new -x509 -nodes -sha1 -days 1780 -subj "/C=US/ST=Washington/L=Port Angeles/O=OpenPrisonEducation/CN=smc.ed" -key web2py.key > web2py.crt && \
	openssl x509 -noout -fingerprint -text < web2py.crt > web2py.info
#	mkdir /etc/uwsgi && \
#	mkdir /var/log/uwsgi

# copy Emperor config files from repo
ADD web2py.ini /etc/uwsgi/web2py.ini
ADD uwsgi-emperor.conf /etc/init/uwsgi-emperor.conf

# copy Supervisor config file from repo
ADD supervisor-app.conf /etc/supervisor/conf.d/


WORKDIR $W2P_DIR
RUN chown -R www-data:www-data $W2P_DIR
USER www-data

# get and install web2py
RUN wget http://web2py.com/examples/static/web2py_src.zip && \
    unzip -o web2py_src.zip -d .. && \
	rm web2py_src.zip && \	
	mv handlers/wsgihandler.py ./wsgihandler.py && \
	chown -R www-data:www-data .

#ADD routes.py $W2P_DIR/routes.py



RUN python -c "from gluon.main import save_password; save_password('$IT_PW',80)" && \
	python -c "from gluon.main import save_password; save_password('$IT_PW',443)"

# Checkout release copy of SMC
RUN git clone https://github.com/frankyrumple/smc.git $W2P_DIR/applications/smc
RUN cp -f $W2P_DIR/applications/smc/routes.py $W2P_DIR/routes.py

# Add a first run file so that next time a page is hit db migration happens
RUN touch $W2P_DIR/applications/smc/.first_run


USER root

RUN chown -R www-data:www-data $W2P_DIR

# Add shortcut to set_admin_password.py
RUN echo '#!/bin/sh\ncd /home/www-data/web2py/applications/smc\npython set_admin_password.py' > /bin/set_admin_password
RUN chmod +x /bin/set_admin_password
RUN chmod +x /home/www-data/web2py/applications/smc/set_admin_password.py



VOLUME ["/home/www-data/web2py/applications/smc/cache", "/home/www-data/web2py/applications/smc/databases", "/home/www-data/web2py/applications/smc/errors", "/home/www-data/web2py/applications/smc/private", "/home/www-data/web2py/applications/smc/static/media", "/home/www-data/web2py/applications/smc/static/uploads"] 
# can't have files as volumes, run the set_admin_password tool
#, "/home/www-data/web2py/parameters_443.py", "/home/www-data/web2py/parameters_80.py"]
EXPOSE 80 443
# 8000
ENV USER=www-data
#ENTRYPOINT python web2py.py
CMD ["supervisord", "-n"]
