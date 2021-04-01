ARG RUBY=2.6-p6.0.4

FROM instructure/ruby-passenger:${RUBY} AS dependencies

#FROM instructure/ruby-passenger:2.4-xenial
##FROM instructure/canvas-lms:stable

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.1"

# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .

#TODO - Auto disable student collaboration features

#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.

ARG POSTGRES_CLIENT=12
ARG ALPINE_MIRROR=http://dl-cdn.alpinelinux.org/alpine
ARG NODE=10.19.0-r0

ENV APP_HOME /usr/src/app/
ENV RAILS_ENV production
ENV NGINX_MAX_UPLOAD_SIZE 50g

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

WORKDIR $APP_HOME

ENV RUBY_VERSION 2.6
ENV YARN_VERSION 1.19.1-1

ENV CANVAS_RELEASE release/2020-11-18.29
#ENV CANVAS_RELEASE release/2020-10-21.32
#ENV CANVAS_RELEASE release/2020-09-23.35
#ENV CANVAS_RELEASE release/2019-10-23.21
#ENV CANVAS_RELEASE release/2019-06-22.25

ENV GEM_HOME /home/docker/.gem/$RUBY_VERSION
ENV PATH $GEM_HOME/bin:$PATH
ENV BUNDLE_APP_CONFIG /home/docker/.bundle


USER root

RUN mkdir ${APP_HOME}; chown -R docker:docker ${APP_HOME}


RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - \
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list \
  && printf 'path-exclude /usr/share/doc/*\npath-exclude /usr/share/man/*' > /etc/dpkg/dpkg.cfg.d/01_nodoc \
  && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  && apt-get update -qq \
  && apt-get install -qqy --no-install-recommends \
       nodejs \
       yarn="$YARN_VERSION" \
       libxmlsec1-dev \
       python-lxml \
       libicu-dev \
       parallel \
       postgresql-client-$POSTGRES_CLIENT \
       unzip \
       pbzip2 \
       fontforge \
       bash \
       nano \
       dos2unix \
       supervisor \       
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /home/docker/.gem/ruby/$RUBY_MAJOR.0
RUN if [ -e /var/lib/gems/$RUBY_MAJOR.0/gems/bundler-* ]; then BUNDLER_INSTALL="-i /var/lib/gems/$RUBY_MAJOR.0"; fi \
  && gem uninstall --all --ignore-dependencies --force $BUNDLER_INSTALL bundler \
  && gem install bundler --no-document -v 1.17.3 \
  && find $GEM_HOME ! -user docker | xargs chown docker:docker


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


WORKDIR $APP_HOME

USER root
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
             log \
             node_modules \
             packages/canvas-media/es \
             packages/canvas-media/lib \
             packages/canvas-media/node_modules \
             packages/canvas-planner/lib \
             packages/canvas-planner/node_modules \
             packages/canvas-rce/canvas \
             packages/canvas-rce/lib \
             packages/canvas-rce/node_modules \
             packages/jest-moxios-utils/node_modules \
             packages/js-utils/es \
             packages/js-utils/lib \
             packages/js-utils/node_modules \
             packages/k5uploader/es \
             packages/k5uploader/lib \
             packages/k5uploader/node_modules \
             packages/old-copy-of-react-14-that-is-just-here-so-if-analytics-is-checked-out-it-doesnt-change-yarn.lock/node_modules \
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

# Fix fonts.googleapis.com links to point to local fonts folder
RUN cd ${APP_HOME} \
   && find . -name "*.html" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.css" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.erb" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \;



#RUN COMPILE_ASSETS_NPM_INSTALL=0 bundle exec rake canvas:compile_assets
RUN COMPILE_ASSETS_NPM_INSTALL=0 JS_BUILD_NO_UGLIFY="$JS_BUILD_NO_UGLIFY" bundle exec rails canvas:compile_assets

#RUN chown -R docker:docker /home/docker
# Make sure docker is the owner for all files
RUN find ${APP_HOME} -not -user docker -exec chown docker:docker {} \+

USER docker


LABEL rebuild=69

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

LABEL rebuild=49
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
 

USER root
    
# Stay root at the end - supervisor will switch back to docker user
VOLUME ["/usr/src/app/tmp", "/usr/src/app/log", "/tmp"]
EXPOSE 3000

CMD ["/usr/src/start.sh"]
