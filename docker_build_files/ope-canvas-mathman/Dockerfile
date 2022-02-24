FROM instructure/node-passenger:12
MAINTAINER Instructure

LABEL rebuild=1

USER root

RUN apt-get update && apt-get install -y --no-install-recommends zip \
  && rm -rf /var/lib/apt/lists/*

COPY package.json package.json
RUN npm install --ignore-scripts --unsafe-perm

COPY nginx.conf /usr/src/nginx/conf.d/headers.conf
COPY . .

USER docker
