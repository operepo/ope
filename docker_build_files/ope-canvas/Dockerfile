ARG RUBY=2.6

FROM instructure/passenger-nginx-alpine:${RUBY} AS dependencies

#FROM instructure/ruby-passenger:2.4-xenial
##FROM instructure/canvas-lms:stable

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.0"

# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .

#TODO - Auto disable student collaboration features

#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.

ARG POSTGRES_CLIENT=12.4
ARG ALPINE_MIRROR=http://dl-cdn.alpinelinux.org/alpine
ARG NODE=10.19.0-r0

ENV APP_HOME /usr/src/app/
ENV RAILS_ENV production
ENV NGINX_MAX_UPLOAD_SIZE 50g

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ENV YARN_VERSION 1.19.1-1

ENV CANVAS_RELEASE release/2020-09-23.35
#ENV CANVAS_RELEASE release/2019-10-23.21
#ENV CANVAS_RELEASE release/2019-06-22.25

ENV GEM_HOME /home/docker/.gem/$RUBY_VERSION
ENV PATH $GEM_HOME/bin:$PATH
ENV BUNDLE_APP_CONFIG /home/docker/.bundle


USER root

RUN mkdir ${APP_HOME}; chown -R docker:docker ${APP_HOME}


RUN set -eux; \
  \
  # Use specific alpine mirror \
  sed -i -E "s|http://dl-cdn.alpinelinux.org/alpine|${ALPINE_MIRROR}|g" /etc/apk/repositories \
  && apk add --no-cache \
    bash \
    coreutils \
    file \
    g++ \
    git \
    icu-dev \
    imagemagick \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    make \
    postgresql-client~=$POSTGRES_CLIENT \
    postgresql-dev~=$POSTGRES_CLIENT \
    # TODO: need to upgrade to python 3 \
    py2-pip \
    python2 \
    ruby-dev \
    sqlite \
    sqlite-dev \
    tzdata \
    xmlsec \
    xmlsec-dev \
    nano \
    dos2unix \
    supervisor \
    unzip \
  && apk add --no-cache --virtual .pbzip2deps \
    bzip2-dev \
  && apk add --no-cache --repository http://mirrors.gigenet.com/alpinelinux/v3.10/main \
    # qti_migration_tool dependency \
    py2-lxml \
  \
  # TODO: extract to its own build in a multi-image workflow \
  # pbzip2 installation \
  && cd /tmp/ \
  && wget -q https://launchpad.net/pbzip2/1.1/1.1.13/+download/pbzip2-1.1.13.tar.gz \
  && tar -xzf pbzip2-1.1.13.tar.gz \
  && cd pbzip2-1.1.13/ \
  && make install \
  && apk del --no-network .pbzip2deps \
  && cd $APP_HOME \
  && rm -r /tmp/pbzip2-1.1.13/ \
  \
  # python symlinks \
  && ln -s /usr/bin/python2 /usr/local/bin/python 



USER docker
# Checkout source for canvaslms
LABEL rebuild=1
RUN cd ${APP_HOME} \
    && git init \
    && git remote add origin https://github.com/instructure/canvas-lms \
    && git fetch origin --no-tags --depth 1 refs/tags/${CANVAS_RELEASE}:refs/tags/${CANVAS_RELEASE} \
    && git checkout ${CANVAS_RELEASE}

USER docker
RUN set -eux; \
  \
  cd ${APP_HOME} \
  # set up bundle config options \
  && bundle config --global build.nokogiri --use-system-libraries \
  && bundle config --global build.ffi --enable-system-libffi \
  && mkdir -p \
    /home/docker/.gem/$RUBY_VERSION \
    /home/docker/.bundle \
  # TODO: --without development \
  && bundle install --jobs $(nproc) \
  && rm -rf $GEM_HOME/cache


USER root
RUN set -eux; \
  \
  # these packages are temporary for generating this image \
  apk add --no-cache --virtual .builddeps --repository $ALPINE_MIRROR/v3.10/main \
    g++ \
    make \
    libsass \
  # these packages stick around in the final image \
  && apk add --no-cache --repository $ALPINE_MIRROR/v3.10/main \
    npm \
    nodejs=${NODE} \
    yarn \
  && apk add --no-cache curl \
  && cd /tmp \
  && curl -Ls https://github.com/instructure/phantomized/releases/download/2.1.1a/dockerized-phantomjs.tar.gz | tar xzv -C / \
  && curl -k -Ls https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 | tar -jxf - \
  && cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs \
  && apk del --no-network curl \
  && rm -rf /tmp/*




#RUN if [ -e /var/lib/gems/$RUBY_MAJOR.0/gems/bundler-* ]; then BUNDLER_INSTALL="-i 
#/var/lib/gems/$RUBY_MAJOR.0"; fi \
#  && gem uninstall --all --ignore-dependencies --force $BUNDLER_INSTALL bundler \
#  && gem install bundler --no-document -v 1.17.3 \
#  && find $GEM_HOME ! -user docker | xargs chown docker:docker

# Make sure this runs during build, will also run at at startup later
#ENV CANVAS_BUILD_CONCURRENCY=1

WORKDIR $APP_HOME


# Fix fonts.googleapis.com links to point to local fonts folder
RUN cd ${APP_HOME} \
   && find . -name "*.html" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.css" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.erb" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \;


# We will need sfnt2woff in order to build fonts
#COPY build/vendor/woff-code-latest.zip ./
RUN cd build/vendor \
  && unzip woff-code-latest.zip -d woff \
  && cd woff \
  && make \
  && cp sfnt2woff /usr/local/bin \
  && cd - \
  && rm -rf woff*

#RUN find gems packages -type d ! -user docker -print0 | xargs -0 chown -h docker:docker

#RUN chown -R docker:docker ${APP_HOME}

USER docker
#RUN bundle install --jobs 12 \
#  && yarn install --pure-lockfile
USER root

RUN set -eux; \
  mkdir -p .yardoc \
             app/stylesheets/brandable_css_brands \
             app/views/info \
             client_apps/canvas_quizzes/dist \
             client_apps/canvas_quizzes/node_modules \
             client_apps/canvas_quizzes/tmp \
             config/locales/generated \
             gems/canvas_i18nliner/node_modules \
             gems/selinimum/node_modules \
             log \
             node_modules \
             packages/canvas-planner/lib \
             packages/canvas-planner/node_modules \
             pacts \
             public/dist \
             public/doc/api \
             public/javascripts/client_apps \
             public/javascripts/compiled \
             public/javascripts/translations \
             reports \
             tmp \
             /home/docker/.bundler/ \
             /home/docker/.cache/yarn \
             /home/docker/.gem/ \
  && (DISABLE_POSTINSTALL=1 yarn install --pure-lockfile || DISABLE_POSTINSTALL=1 yarn install --pure-lockfile --network-concurrency 1) \
  && yarn cache clean  

# INSTALL QTIMigrationTool
RUN mkdir ${APP_HOME}/vendor \
	&& cd ${APP_HOME}/vendor \
	&& git clone https://github.com/instructure/QTIMigrationTool.git QTIMigrationTool \
	&& chmod +x QTIMigrationTool/migrate.py
    
#RUN rm -rf node_modules \
#    && rm -rf gems/**/node_modules \
#    && npm cache clean    

USER root

# Make sure docker is the owner for all files
RUN find ${APP_HOME} -not -user docker -exec chown docker:docker {} \+

# update Gemfile.lock in cases where a lock file was pulled in during the `COPY . $APP_HOME` step
#RUN bundle lock --update


# TODO: switch to canvas:compile_assets_dev once we stop using this Dockerfile in production/e2e
#RUN yarn upgrade
RUN yarn postinstall

FROM dependencies AS webpack-final
ARG JS_BUILD_NO_UGLIFY=0

#RUN COMPILE_ASSETS_NPM_INSTALL=0 bundle exec rake canvas:compile_assets
RUN COMPILE_ASSETS_NPM_INSTALL=0 JS_BUILD_NO_UGLIFY="$JS_BUILD_NO_UGLIFY" bundle exec rails canvas:compile_assets

#RUN chown -R docker:docker /home/docker

USER docker


LABEL rebuild=66

COPY amazon_s3.yml config/amazon_s3.yml
COPY delayed_jobs.yml config/delayed_jobs.yml
COPY file_store.yml config/file_store.yml
COPY security.yml.tmpl config/security.yml.tmpl
COPY external_migration.yml config/external_migration.yml

COPY database.yml.tmpl config/database.yml.tmpl
COPY redis.yml config/redis.yml
COPY cache_store.yml config/cache_store.yml
COPY production-local.rb config/environments/production-local.rb
COPY outgoing_mail.yml.tmpl config/outgoing_mail.yml.tmpl

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY domain.yml.tmpl /usr/src/app/config/domain.yml.tmpl
COPY puma.rb /usr/src/app/config/puma.rb
COPY rack.rb /usr/src/app/config/initializers/rack.rb
COPY dynamic_settings.yml.tmpl /usr/src/app/config/dynamic_settings.yml.tmpl

LABEL rebuild=24
COPY dbinit.sh /usr/src/dbinit.sh
COPY start.sh /usr/src/start.sh
COPY ope.rake lib/tasks/ope.rake

COPY ViewerJS/ /usr/src/app/public/vendor/ViewerJS/

# Copy googleapi fonts into local folder
COPY fonts/* /usr/src/app/public/fonts/

# Copy mathjax files into local folder
COPY ajax /usr/src/app/public/ajax/
# Extensions need to be a the root
COPY ajax/libs/mathjax/2.7.5/extensions /usr/src/app/public/extensions/


USER root


RUN echo "Settings file permissions..." \
    && mkdir /tmp/attachment_fu \
    && chown -R docker:docker /tmp/attachment_fu /usr/src/app/log \
    && chmod 755 /usr/src/*.sh \
    && dos2unix /usr/src/*.sh
 
# Make sure docker is the owner for all files
RUN find ${APP_HOME} -not -user docker -exec chown docker:docker {} \+


USER root
    
# Stay root at the end - supervisor will switch back to docker user
VOLUME ["/usr/src/app/tmp", "/usr/src/app/log", "/tmp"]
EXPOSE 3000

CMD ["/usr/src/start.sh"]
