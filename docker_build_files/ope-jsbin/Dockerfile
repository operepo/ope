FROM node:0.10

RUN npm install -g jsbin@3.11.23

#ENV JSBIN_CONFIG=/usr/local/lib/node_modules/jsbin/config.default.json 
ENV JSBIN_CONFIG=/config/jsbin.json
ENV VIRTUAL_HOST=jsbin.ed

RUN mkdir /config \
	&& mkdir /data
LABEL rebuild=5
COPY jsbin.json.template /config/jsbin.json.template
COPY start.sh /start.sh
RUN chmod +x /start.sh

VOLUME ["/data"]

#CMD jsbin 
CMD /start.sh
