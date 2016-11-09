FROM ubuntu:16.04
# ope-codecombat - CodeCombat Learning Environment
# Build with docker build -t ope-codecombat .

#INSTRUCTIONS
# Build the codecombat container and run it with the docker-compose command


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="CodeCombat Learning Environment - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

ENV DEBIAN_FRONTEND noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL C
ENV TERM=xterm

ENV COCO_MONGO_HOST localhost
ENV NODE_ENV development


RUN groupadd -r coco -g 921 && \
    adduser --uid 921 --system --gid 921 --home /home/coco coco && \
    adduser coco sudo

RUN \
	apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927 \
	&& echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.2.list \
	&& apt-get update \
	&& apt-get -y install vim wget nano make build-essential curl git zlib1g-dev python2.7 libkrb5-dev g++ make supervisor ruby1.9.1 npm mongodb-org dos2unix nodejs-legacy \
	&& apt-get clean

# Install nodejs
#RUN cd /tmp \
#	&& wget http://nodejs.org/dist/node-latest.tar.gz \
#	&& tar xvzf node-latest.tar.gz \
#	&& rm -f node-latest.tar.gz \
#	&& cd node-v* \
#	&& ./configure \
#	&& CXX="g++ -Wno-unused-local-typedefs" make \
#	&& CXX="g++ -Wno-unused-local-typedefs" make install \
#	&& cd /tmp \
#	&& rm -rf /tmp/node-v* \
#	&& npm -v
	

RUN mkdir -p /home/coco \
	&& cd /home/coco \
	&& git clone https://github.com/codecombat/codecombat.git \
	&& cd /home/coco/codecombat \
	&& npm config set registry https://registry.cnpmjs.org \
	&& npm config set python python2.7 \
	&& npm install --save nan@latest \
	&& npm install -g bower --allow-root \
	&& npm install -g brunch \
	&& npm install -g geoip-lite \
	&& npm install -g nodemon \
	&& npm install -g coffee-script@1.9.x \
	&& npm install -g uglify-js@2.5.0 \
	&& npm install -g node-gyp \
	&& SASS_BINARY_SITE=https://npm.taobao.org/mirrors/node-sass/ npm install --phantomjs_cdnurl=http://cnpmjs.org/downloads

RUN cd /home/coco/codecombat \
	&& gem install sass \
	&& bower --allow-root install \
	&& brunch build --env fast \
	&& npm install

LABEL rebuild=12
ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf
ADD start.sh /home/coco/start.sh
ADD mongod.conf /etc/mongod.conf
RUN chmod +x /home/coco/start.sh
RUN dos2unix /home/coco/*.sh
#RUN chown -R coco:coco /home/coco \
#	&& chown -R coco:coco /root

VOLUME ["/home/coco/codecombat/mongo", "/home/coco/codecombat/data"]
EXPOSE 3000
#CMD ["/home/coco/start.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
	
	
	
