FROM instructure/core:focal
#FROM instructure/ruby-passenger:${RUBY} as dependencies

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.4"

# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .

#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.

ARG POSTGRES_CLIENT=12

ENV APP_HOME /usr/src/app/
ENV RAILS_ENV production
ENV NGINX_MAX_UPLOAD_SIZE 50g

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ARG CANVAS_RAILS=6.1
ENV CANVAS_RAILS=${CANVAS_RAILS}

ENV RUBY_MAJOR 2.7
ENV RUBYGEMS_VERSION 3.1.3
#ENV RUBYGEMS_VERSION 3.1.5
ENV RUBY_VERSION $RUBY_MAJOR
ENV YARN_VERSION 1.19.1-1
ENV BUNDLER_VERSION 2.2.33
#ENV BUNDLER_VERSION 2.2.17


ENV CANVAS_RELEASE prod
#ENV CANVAS_RELEASE release/2022-05-25.135
#ENV CANVAS_RELEASE release/2022-01-19.127
#ENV CANVAS_RELEASE release/2021-12-15.42
#ENV CANVAS_RELEASE release/2020-10-21.32

ENV GEM_HOME /home/docker/.gem/$RUBY_MAJOR.0
ENV PATH $GEM_HOME/bin:$PATH
ENV BUNDLE_APP_CONFIG /home/docker/.bundle

WORKDIR $APP_HOME

USER root

ARG USER_ID
# This step allows docker to write files to a host-mounted volume with the correct user permissions.
# Without it, some linux distributions are unable to write at all to the host mounted volume.
RUN if [ -n "$USER_ID" ]; then usermod -u "${USER_ID}" docker \
        && chown --from=9999 docker /usr/src/nginx /usr/src/app -R; fi

RUN mkdir -p ${APP_HOME}; chown -R docker:docker ${APP_HOME}


RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common \
 && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

#RUN apt-add-repository -y ppa:brightbox/ruby-ng \
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list \
  && printf 'path-exclude /usr/share/doc/*\npath-exclude /usr/share/man/*' > /etc/dpkg/dpkg.cfg.d/01_nodoc \
  && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  && apt-get update -qq \
  && apt-get install -qqy --no-install-recommends \
       ruby$RUBY_MAJOR \
       ruby$RUBY_MAJOR-dev \
       curl \
       make \
       imagemagick \
       libbz2-dev \
       libcurl4-openssl-dev \
       libevent-dev \
       libffi-dev \
       libglib2.0-dev \
       libjpeg-dev \
       libgdbm6 \
       libgdbm-dev \
       libdb-dev \
       libmagickcore-dev \
       libmagickwand-dev \
       libmysqlclient-dev \
       libncurses-dev \
       libpq-dev \
       libreadline-dev \
       libsqlite3-dev \
       libssl-dev \
       libxml2-dev \
       libxslt-dev \
       libyaml-dev \
       zlib1g-dev \
       nodejs \
       yarn="$YARN_VERSION" \
       libxmlsec1-dev \
       python-lxml \
       python3-lxml \
       libicu-dev \
       parallel \
       postgresql-client-$POSTGRES_CLIENT \
       unzip \
       pbzip2 \
       fontforge \
       autoconf \
       automake \
       git \
       build-essential \
       g++ \
       gcc \
       bison \
       python2 \
       python-is-python2 \
       bash \
       nano \
       dos2unix \
       supervisor \
       sudo \
       file \
       rsync \
       python3-pip \
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/ \
  && mkdir -p /home/docker/.gem/ruby/$RUBY_MAJOR.0

RUN python3 -m pip install watchfiles

ENV BUNDLE_APP_CONFIG /home/docker/.bundle

RUN echo 'gem: --no-document' >> /home/docker/.gemrc \
 &&  echo 'gem: --no-document' >> /root/.gemrc \
 && mkdir -p /home/docker/.gem/ruby/$RUBY_MAJOR.0/build_info \
             /home/docker/.gem/ruby/$RUBY_MAJOR.0/cache \
             /home/docker/.gem/ruby/$RUBY_MAJOR.0/doc \
             /home/docker/.gem/ruby/$RUBY_MAJOR.0/extensions \
             /home/docker/.gem/ruby/$RUBY_MAJOR.0/gems \
             /home/docker/.gem/ruby/$RUBY_MAJOR.0/specifications

#RUN gem install --no-document -i /var/lib/gems/$RUBY_MAJOR.0 bundler -v $BUNDLER_VERSION \
#gem update --no-document --system $RUBYGEMS_VERSION \
# Move bundler off default, then unistall it, then reinstall our version
RUN mv /usr/lib/ruby/gems/2.7.0/specifications/default/bundler*.gemspec /usr/lib/ruby/gems/2.7.0/specifications/ \ 
  && gem uninstall --all --ignore-dependencies --force -i /var/lib/gems/$RUBY_MAJOR.0 bundler || true \
  && gem install --no-document --default bundler -v $BUNDLER_VERSION \
  && gem install --no-document bundler -v $BUNDLER_VERSION


# Checkout source for canvaslms
LABEL rebuild=1
USER docker
RUN cd ${APP_HOME} \
    && git config --global --add safe.directory ${APP_HOME} \
    && git init \
    && git remote add origin https://github.com/instructure/canvas-lms \
    #&& git fetch origin --no-tags --depth 1 refs/tags/${CANVAS_RELEASE}:refs/tags/${CANVAS_RELEASE} \
    && git fetch --no-tags --depth 1 origin ${CANVAS_RELEASE} \
    && git checkout ${CANVAS_RELEASE}


# NOTE - Need some dummy config files in place - these should get overwritten later
RUN cd ${APP_HOME}/config \
  && cp amazon_s3.yml.example amazon_s3.yml \
  && cp database.yml.example database.yml \
  && cp delayed_jobs.yml.example delayed_jobs.yml \
  && cp domain.yml.example domain.yml \
  && cp file_store.yml.example file_store.yml \
  && cp outgoing_mail.yml.example outgoing_mail.yml \
  && cp security.yml.example security.yml \
  && cp external_migration.yml.example external_migration.yml \
  && cp dynamic_settings.yml.example dynamic_settings.yml
 



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


# INSTALL QTIMigrationTool
RUN mkdir ${APP_HOME}/vendor \
	&& cd ${APP_HOME}/vendor \
	&& git clone https://github.com/instructure/QTIMigrationTool.git QTIMigrationTool \
	&& chmod +x QTIMigrationTool/migrate.py

RUN set -eux; \
  mkdir -p \
    .yardoc \
    app/stylesheets/brandable_css_brands \
    app/views/info \
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
    public/javascripts/translations \
    reports \
    tmp \
    /home/docker/.bundle/ \
    /home/docker/.cache/yarn \
    /home/docker/.gem/ \
  && touch app/stylesheets/_brandable_variables_defaults_autogenerated.scss Gemfile.lock


# Make sure docker is the owner for all files
RUN find ${APP_HOME} -not -user docker -exec chown docker:docker {} \+ || true
RUN chown -R docker:docker /home/docker/.bundle /home/docker/.gem /home/docker/.cache /usr/lib/ruby/gems || true

#RUN npm install -g npm@latest && npm cache clean --force

USER docker

RUN set -eux; \
  \
  cd ${APP_HOME} \
  && gem uninstall --ignore-dependencies --force -i /usr/lib/ruby/gems/2.7.0 bundler -v 2.1.2 || true \
  && gem install --no-document bundler -v $BUNDLER_VERSION \
  #&& gem install rubygems-update \
  #&& update_rubygems \
  ##&& gem update --system \
  && bundle config --global build.nokogiri --use-system-libraries \
  && bundle config --global build.ffi --enable-system-libffi \
  && bundler install --jobs $(nproc) \
  && rm -rf $GEM_HOME/cache


    
#RUN rm -rf node_modules \
#    && rm -rf gems/**/node_modules \
#    && npm cache clean    

# update Gemfile.lock in cases where a lock file was pulled in during the `COPY . $APP_HOME` step
#RUN bundle lock --update


# TODO: switch to canvas:compile_assets_dev once we stop using this Dockerfile in production/e2e
#RUN yarn global add gulp --no-bin-links \
#  && yarn global add yarn-deduplicate --no-bin-links \
#  #&& npx browserslist@latest --update-db \
#  #&& npm --depth 20 update --save caniuse-lite browserslist \
#  && yarn install

# Clean up node_modules/cached stuff....
#RUN git clean packages public spec/javascripts node_modules coverage-js gems/*/node_modules packages/*node_modules ui -Xfd \
#  && rm -rfv gems/plugins/*/node_modules

# Runs as part of compile_assets  yarn:install
#RUN yarn upgrade
#RUN yarn postinstall
RUN touch Gemfile.lock \
  && yarn install --pure-lockfile

USER docker
ARG JS_BUILD_NO_UGLIFY=0
#CANVAS_BUILD_CONCURRENCY=1
#DISABLE_HAPPYPACK=1
#RUN COMPILE_ASSETS_NPM_INSTALL=0 bundle exec rake canvas:compile_assets
#RUN COMPILE_ASSETS_NPM_INSTALL=0 JS_BUILD_NO_UGLIFY="$JS_BUILD_NO_UGLIFY" bundle exec rails canvas:compile_assets
#RUN CANVAS_BUILD_CONCURRENCY=1 DISABLE_HAPPYPACK=1 COMPILE_ASSETS_NPM_INSTALL=0 JS_BUILD_NO_UGLIFY="$JS_BUILD_NO_UGLIFY" \
# Individual commands that compile_assets runs
#RUN bundle exec rake js:yarn_install \
#  && bundle exec rake css:compile \
#  && bundle exec rake css:styleguide \
#  && bundle exec rake i18n:generate_js \
#  && bundle exec rake js:webpack_development \
#  && bundle exec rake doc:api
# Don't need or non existent
#  && bundle exec rake js:build_client_apps \
# yarn run gulp rev
#RUN bundle exec rake js:webpack_production --trace
# COMPILE_ASSETS_NPM_INSTALL  COMPILE_ASSETS_API_DOCS
# COMPILE_ASSETS_CSS  COMPILE_ASSETS_STYLEGUIDE
# RAILS_LOAD_ALL_LOCALES  COMPILE_ASSETS_BUILD_JS
# COMPILE_ASSETS_BRAND_CONFIGS  USE_OPTIMIZED_JSJS_BUILD_NO_FALLBACK
# JS_BUILD_NO_FALLBACK   JS_BUILD_NO_UGLIFY

RUN COMPILE_ASSETS_BRAND_CONFIGS=0 bundle exec rake canvas:compile_assets --trace


USER docker
#RUN chown -R docker:docker /home/docker
# Make sure docker is the owner for all files
#RUN find ${APP_HOME} -not -user docker -exec chown docker:docker {} \+

# Fix fonts.googleapis.com links to point to local fonts folder
RUN cd ${APP_HOME} \
   && find . -name "*.html" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.css" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.erb" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -name "*.html" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/' {} \; \
   && find . -name "*.css" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/' {} \; \
   && find . -name "*.erb" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/' {} \;


USER docker

LABEL rebuild=92

COPY amazon_s3.yml config/amazon_s3.yml
COPY delayed_jobs.yml config/delayed_jobs.yml
COPY file_store.yml config/file_store.yml
COPY security.yml.tmpl config/security.yml.tmpl
COPY external_migration.yml config/external_migration.yml

COPY database.yml.tmpl config/database.yml.tmpl
COPY redis.yml config/redis.yml
COPY cache_store.yml config/cache_store.yml
COPY production-local.rb config/environments/production.rb
COPY outgoing_mail.yml.tmpl config/outgoing_mail.yml.tmpl

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY domain.yml.tmpl /usr/src/app/config/domain.yml.tmpl
COPY puma.rb /usr/src/app/config/puma.rb
COPY rack.rb /usr/src/app/config/initializers/rack.rb
COPY dynamic_settings.yml.tmpl /usr/src/app/config/dynamic_settings.yml.tmpl
COPY mime_types.rb /usr/src/app/config/initializers/mime_types.rb
COPY session_store.yml.tmpl /usr/src/app/config/session_store.yml.tmpl


LABEL rebuild=57
COPY sync_static_files.py /usr/src/sync_static_files.py
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
    && mkdir -p /tmp/attachment_fu \
    && mkdir -p /usr/src/app/log \
    && chown -R docker:docker /tmp/attachment_fu /usr/src/app/log \
    && chmod 755 /usr/src/*.sh \
    && dos2unix /usr/src/*.sh



USER root
    
# Stay root at the end - supervisor will switch back to docker user
VOLUME ["/usr/src/app/tmp", "/usr/src/app/log", "/tmp", "/usr/src/app/sendfile"]
EXPOSE 3000

CMD ["/usr/src/start.sh"]
