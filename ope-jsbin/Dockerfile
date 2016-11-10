FROM node:0.10

RUN npm install -g jsbin

#ENV JSBIN_CONFIG=/usr/local/lib/node_modules/jsbin/config.default.json 
ENV JSBIN_CONFIG=/config/jsbin.json 

RUN mkdir /config \
	&& mkdir /data
LABEL rebuild=3
COPY jsbin.json /config/jsbin.json

VOLUME ["/data"]

CMD jsbin 