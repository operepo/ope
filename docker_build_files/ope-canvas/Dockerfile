# ope-canvas - Canvas LMS System for Open Prison Education
# Build with docker build -t ope-canvas .
#
# Toolchain follows the upstream canvas-lms Dockerfile for CANVAS_RELEASE (ruby-passenger:3.4-jammy,
# node 20, yarn 1.19.1 via corepack, bundler 2.5.10) - OPE additions are marked with "OPE:".
#
# NOTE - existing databases: Canvas squashes old migrations. A database must already have migration
# 20250930000003 before this release will migrate it (see db/migrate/*_validate_migration_integrity.rb).
# Databases from older OPE images (release/2022-07-06) need to step through intermediate releases first.

ARG RUBY=3.4
FROM instructure/ruby-passenger:${RUBY}-jammy

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="2.0"

# OPE: do NOT re-declare "ARG RUBY" here (upstream does) - build args are exported as env vars in every RUN,
# and rake/ffi-compiler use $RUBY as the ruby executable, so native gem builds (scrypt) run "3.4 ..." and fail.
# Keep RUBY_SERIES in sync with the RUBY arg above.
ARG RUBY_SERIES=3.4
# OPE: client matches the ope-postgresql server version (pg_dump etc. must be >= server)
ARG POSTGRES_CLIENT=18

ENV APP_HOME /usr/src/app/
ENV RAILS_ENV production
ENV NGINX_MAX_UPLOAD_SIZE 50g

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

ARG CANVAS_RAILS=8.0
ENV CANVAS_RAILS=${CANVAS_RAILS}

ENV NODE_MAJOR 20
# OPE: match "BUNDLED WITH" in canvas' Gemfile.lock (upstream's dev Dockerfile pins 2.5.10, which re-resolves
# the lockfiles and then bundler-multilock fails with "platforms ... do not match the parent lockfile")
ENV BUNDLER_VERSION 2.6.7

# release/2026-04-22.394 = the tree Instructure had on the canvas-lms "prod" branch when the public
# GitHub mirror stopped updating (2026-04-30)
ENV CANVAS_RELEASE release/2026-04-22.394
#ENV CANVAS_RELEASE release/2022-07-06.145

# QTIMigrationTool (python3) - pinned so rebuilds are repeatable (2026-03-23: exclude time_limit <= 0)
ENV QTI_MIGRATION_TOOL_COMMIT aab28af7a05142140c6fd2f45ed67a4c925a7d1b

ENV GEM_HOME /home/docker/.gem/$RUBY_SERIES
ENV PATH ${APP_HOME}bin:$GEM_HOME/bin:$PATH
ENV BUNDLE_APP_CONFIG /home/docker/.bundle

WORKDIR $APP_HOME

USER root

ARG USER_ID
# This step allows docker to write files to a host-mounted volume with the correct user permissions.
# Without it, some linux distributions are unable to write at all to the host mounted volume.
RUN if [ -n "$USER_ID" ]; then usermod -u "${USER_ID}" docker \
        && chown --from=9999 docker /usr/src/nginx /usr/src/app -R; fi

RUN mkdir -p ${APP_HOME}; chown -R docker:docker ${APP_HOME}

# Same package set as upstream + OPE extras (supervisor, rsync, imagemagick, python3-pip, editors/tools)
RUN mkdir -p /etc/apt/keyrings \
  && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
  && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
  && printf 'path-exclude /usr/share/doc/*\npath-exclude /usr/share/man/*' > /etc/dpkg/dpkg.cfg.d/01_nodoc \
  && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  && add-apt-repository ppa:git-core/ppa -ny \
  && apt-get update -qq \
  && apt-get install -qqy --no-install-recommends \
       nodejs \
       libxmlsec1-dev \
       python3-lxml \
       python-is-python3 \
       libicu-dev \
       libidn11-dev \
       parallel \
       postgresql-client-$POSTGRES_CLIENT \
       tzdata \
       unzip \
       pbzip2 \
       fontforge \
       git \
       build-essential \
       # OPE: extras
       imagemagick \
       supervisor \
       rsync \
       python3-pip \
       nano \
       dos2unix \
       sudo \
       file \
  && rm -rf /var/lib/apt/lists/*

# OPE: file watcher used by sync_static_files.py (keeps the sendfile copy of public/ up to date)
RUN python3 -m pip install --no-cache-dir watchfiles

RUN gem install bundler --no-document -v $BUNDLER_VERSION \
  && find $GEM_HOME ! -user docker | xargs -r chown docker:docker
RUN npm install -g npm@9.8.1 && npm cache clean --force

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare yarn@1.19.1 --activate

# Checkout source for canvaslms
LABEL rebuild=2
USER docker
RUN cd ${APP_HOME} \
    && git config --global --add safe.directory ${APP_HOME} \
    && git init \
    && git remote add origin https://github.com/instructure/canvas-lms \
    && git fetch origin --no-tags --depth 1 refs/tags/${CANVAS_RELEASE}:refs/tags/${CANVAS_RELEASE} \
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
RUN cd build/vendor \
  && unzip woff-code-latest.zip -d woff \
  && cd woff \
  && make \
  && cp sfnt2woff /usr/local/bin \
  && cd - \
  && rm -rf woff*

# INSTALL QTIMigrationTool (python3 - canvas runs vendor/QTIMigrationTool/migrate.py for QTI imports)
RUN mkdir -p ${APP_HOME}/vendor \
	&& cd ${APP_HOME}/vendor \
	&& git clone https://github.com/instructure/QTIMigrationTool.git QTIMigrationTool \
	&& cd QTIMigrationTool \
	&& git checkout ${QTI_MIGRATION_TOOL_COMMIT} \
	&& chmod +x migrate.py \
	&& ./migrate.py --version

RUN set -eux; \
  mkdir -p \
    .yardoc \
    app/stylesheets/brandable_css_brands \
    app/views/info \
    config/locales/generated \
    log \
    node_modules \
    packages/js-utils/es \
    packages/js-utils/lib \
    packages/js-utils/node_modules \
    pacts \
    public/dist \
    public/javascripts/translations \
    reports \
    tmp \
    /home/docker/.bundle/ \
    /home/docker/.cache/yarn \
    /home/docker/.gem/ \
  && touch app/stylesheets/_brandable_variables_defaults_autogenerated.scss Gemfile.lock

# Make sure docker is the owner for all files
RUN find ${APP_HOME} -not -user docker -exec chown docker:docker {} \+ || true
RUN chown -R docker:docker /home/docker/.bundle /home/docker/.gem /home/docker/.cache || true

USER docker

RUN set -eux; \
  cd ${APP_HOME} \
  && bundle config --global build.nokogiri --use-system-libraries \
  && bundle config --global build.ffi --enable-system-libffi \
  # NOTE: don't set "frozen" - bundler-multilock generates Gemfile.rails80.plugins.lock (not committed) on install
  && bundle install --jobs $(nproc) \
  && rm -rf $GEM_HOME/cache

# yarn 1 + canvas' nested workspace installs can race on the shared cache ("Extracting tar content ...
# file appears to be corrupt") - retry with a longer network timeout before giving up
RUN ok=0; for i in 1 2 3; do \
      if yarn install --pure-lockfile --network-timeout 600000; then ok=1; break; fi; \
      echo "=== yarn install failed (attempt $i) - retrying ==="; sleep 10; \
    done; \
    [ "$ok" = "1" ] && yarn cache clean

# OPE: release/2026-04-22.394 imports @instructure/platform-alerts (ui/features/discovery_page/.../ConfigureModal.tsx)
# but the package isn't in package.json / yarn.lock, so rspack fails with "Module not found". Canvas' own
# @canvas/alerts/react/FlashAlert exports the same showFlashAlert({message, type}) - point the import there.
# Only applied while the package is missing, so a later release that ships it is left alone.
RUN if [ ! -d node_modules/@instructure/platform-alerts ]; then \
      grep -rl "@instructure/platform-alerts" ui packages --include=*.ts --include=*.tsx --include=*.js --include=*.jsx 2>/dev/null \
        | xargs -r sed -i "s#'@instructure/platform-alerts'#'@canvas/alerts/react/FlashAlert'#g"; \
    fi

# OPE: equation editor (MathLive) fonts. canvas-rce injects MathLive's @font-face css as an inline <style> with
# url(fonts/KaTeX_*.woff2) (upstream TODO "restore import after switch from webpack to rslib"), so the browser
# resolves it against the page url (/courses/1/pages/x/fonts/KaTeX_Main-Regular.woff2 -> 404). Point it at the
# copy made after compile_assets below. Only matches while upstream still has the relative urls.
RUN grep -rl "url(fonts/KaTeX_" packages/canvas-rce/src packages/canvas-rce/es 2>/dev/null \
      | xargs -r sed -i "s#url(fonts/KaTeX_#url(/dist/webpack-production/fonts/KaTeX_#g"

# Build JS/CSS assets (brand configs are generated at startup by start.sh / ope.rake)
# JS_BUILD_NO_FALLBACK=1 - skip the non-optimized "development" JS bundle (production only serves the
# optimized one - USE_OPTIMIZED_JS=true in production.rb). Saves build time and image size.
RUN COMPILE_ASSETS_BRAND_CONFIGS=0 JS_BUILD_NO_FALLBACK=1 bundle exec rake canvas:compile_assets --trace

# OPE: MathLive's fonts + keypress sounds, served locally. MathLive's own loader looks for ./fonts and ./sounds
# next to its JS chunk (/dist/webpack-production/), and the patched @font-face css above uses the same folder.
RUN ML=$(dirname "$(find node_modules packages/canvas-rce/node_modules -maxdepth 2 -path '*/mathlive/package.json' 2>/dev/null | head -1)") \
    && cp -r "$ML/dist/fonts" "$ML/dist/sounds" public/dist/webpack-production/ \
    && test -f public/dist/webpack-production/fonts/KaTeX_Main-Regular.woff2

# OPE: files the compiled JS would load from public CDNs (video player hls.js/dash.js, webcam background-blur
# MediaPipe wasm + model, emoji picker sprite sheet) are put in public/ope-vendor/ and the urls rewritten.
# Fails the build if a newer canvas release asks for a different version - update the script's variables.
COPY vendor_cdn_assets.sh /usr/src/vendor_cdn_assets.sh
RUN bash /usr/src/vendor_cdn_assets.sh

# Fix fonts.googleapis.com links to point to local fonts folder
RUN cd ${APP_HOME} \
   && find . -path ./node_modules -prune -o -name "*.html" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -path ./node_modules -prune -o -name "*.css" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -path ./node_modules -prune -o -name "*.erb" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/' {} \; \
   && find . -path ./node_modules -prune -o -name "*.html" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/' {} \; \
   && find . -path ./node_modules -prune -o -name "*.css" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/' {} \; \
   && find . -path ./node_modules -prune -o -name "*.erb" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/' {} \;

LABEL rebuild=112

COPY amazon_s3.yml config/amazon_s3.yml
COPY delayed_jobs.yml config/delayed_jobs.yml
COPY file_store.yml config/file_store.yml
COPY security.yml.tmpl config/security.yml.tmpl
COPY external_migration.yml config/external_migration.yml

COPY database.yml.tmpl config/database.yml.tmpl
COPY redis.yml config/redis.yml
COPY cache_store.yml config/cache_store.yml
# OPE: production.rb loads config/environments/production-*.rb - OPE settings are an add-on, upstream file stays
COPY production-local.rb config/environments/production-local.rb
COPY outgoing_mail.yml.tmpl config/outgoing_mail.yml.tmpl

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY domain.yml.tmpl /usr/src/app/config/domain.yml.tmpl
COPY puma.rb /usr/src/app/config/puma.rb
# OPE: extra initializers (upstream rack.rb / mime_types.rb are left alone)
COPY rack.rb /usr/src/app/config/initializers/ope_rack.rb
COPY mime_types.rb /usr/src/app/config/initializers/ope_mime_types.rb
COPY dynamic_settings.yml.tmpl /usr/src/app/config/dynamic_settings.yml.tmpl
COPY session_store.yml.tmpl /usr/src/app/config/session_store.yml.tmpl

LABEL rebuild=59
COPY sync_static_files.py /usr/src/sync_static_files.py
COPY dbinit.sh /usr/src/dbinit.sh
COPY start.sh /usr/src/start.sh
COPY write_credentials.rb /usr/src/write_credentials.rb
COPY ope.rake lib/tasks/ope.rake

COPY ViewerJS/ /usr/src/app/public/vendor/ViewerJS/

# Copy googleapi fonts into local folder
COPY fonts/* /usr/src/app/public/fonts/

# Copy mathjax files into local folder (2.7.7 for current canvas, 2.7.5 kept for older builds)
COPY ajax /usr/src/app/public/ajax/
# Fallback - if MathJax can't detect its root it asks for /extensions/... from the site root.
COPY ajax/libs/mathjax/2.7.7/extensions /usr/src/app/public/extensions/

USER root

RUN echo "Settings file permissions..." \
    && mkdir -p /tmp/attachment_fu \
    && mkdir -p /usr/src/app/log \
    && chown -R docker:docker /tmp/attachment_fu /usr/src/app/log /usr/src/app/config /usr/src/app/lib/tasks /usr/src/app/public \
    && chmod 755 /usr/src/*.sh \
    && dos2unix /usr/src/*.sh

# Stay root at the end - supervisor will switch back to docker user
VOLUME ["/usr/src/app/tmp", "/usr/src/app/log", "/tmp", "/usr/src/app/sendfile", "/usr/src/app/keys"]
EXPOSE 3000

CMD ["/usr/src/start.sh"]
