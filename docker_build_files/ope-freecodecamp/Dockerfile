FROM node:0.10
TODO - still converting from jsbin
RUN npm install -g gulp \
	&& npm install -g node-gyp


RUN mkdir /freecodecamp \
	&& cd /freecodecamp \
	&& git clone https://github.com/freeCodeCamp/freeCodeCamp.git \
	
	

	
#ENV JSBIN_CONFIG=/usr/local/lib/node_modules/jsbin/config.default.json 
ENV JSBIN_CONFIG=/config/jsbin.json
ENV VIRTUAL_HOST=freecodecamp.ed

RUN mkdir /config \
	&& mkdir /data
LABEL rebuild=5

COPY start.sh /start.sh
RUN chmod +x /start.sh

VOLUME ["/data"]

#CMD jsbin 
CMD /start.sh