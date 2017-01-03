FROM ubuntu:16.04
# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .

#TODO - Auto disable student collaboration features

#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.

# To copy to offline server use the setup tool

# Set the locale to avoid active_model_serializers bundler install failure
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
#ENV LANG=C.UTF-8
ENV TERM=xterm
ENV BUNDLER_VERSION 1.12.5

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Canvas LMS by Instructure - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.2"


ENV RAILS_ENV production
ENV GEM_HOME /opt/canvas/.gems

# add nodejs and recommended ruby repos
RUN apt-get update \
	&& apt-get -y install --no-install-recommends software-properties-common python-software-properties \
    && add-apt-repository -y ppa:brightbox/ruby-ng \
	&& apt-get update \
    && apt-get -y install --no-install-recommends curl software-properties-common nano \
		apt-transport-https ca-certificates software-properties-common language-pack-en locales \
		psmisc build-essential python \
		ruby2.3 ruby2.3-dev make imagemagick supervisor vim dos2unix python-lxml \
		libbz2-dev libcurl4-openssl-dev libevent-dev libffi-dev libglib2.0-dev libjpeg-dev \
		libmagickcore-dev libmagickwand-dev libmysqlclient-dev libncurses-dev libreadline-dev \
		libssl-dev libyaml-dev file  \
        zlib1g-dev libxml2-dev libxslt1-dev libsqlite3-dev postgresql-client libpq5 \
		libpq-dev libxmlsec1-dev curl make g++ git unzip fontforge \
	&& rm -rf /var/lib/apt/lists/*\
	&& apt-get clean && rm -Rf /var/cache/apt
	
RUN dpkg-reconfigure locales

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash \    
	&& apt-get -y install --no-install-recommends nodejs \
	&& npm install -g gulp \
	&& npm install --unsafe-perm -g coffee-script@1.6.2 \
	&& npm install -g node-sass 
	
#  \

RUN mkdir -p /opt/canvas/canvas-lms \
	&& cd /opt/canvas \
    && git clone https://github.com/instructure/canvas-lms.git

WORKDIR /opt/canvas/canvas-lms

RUN mkdir -p /opt/canvas/fonts \
  && cd /opt/canvas/fonts \
  && curl -O  https://people-mozilla.org/~jkew/woff/woff-code-latest.zip \
  && unzip woff-code-latest.zip \
  && make \
  && cp sfnt2woff /usr/local/bin \
  && echo "sfnt2woff installed" \
  && cd /opt/canvas/canvas-lms \
  && gem install bundler --no-document -v $BUNDLER_VERSION \
  && gem install i18nliner \
  && npm install i18nliner \
  && $GEM_HOME/bin/bundle install --without="mysql"
  #&& find $GEM_HOME ! -user docker | xargs chown docker:docker
#--force $BUNDLER_INSTALL bundler \
#&& gem uninstall --all --ignore-dependencies \
#&& gem update

RUN groupadd -r canvasuser -g 433 && \
    adduser --uid 431 --system --gid 433 --home /opt/canvas canvasuser && \
    adduser canvasuser sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


RUN for config in amazon_s3 delayed_jobs domain file_store security external_migration \
       ; do cp config/$config.yml.example config/$config.yml \
       ; done

LABEL rebuild=7

COPY database.yml config/database.yml
COPY redis.yml config/redis.yml
COPY cache_store.yml config/cache_store.yml
COPY production-local.rb config/environments/production-local.rb
COPY outgoing_mail.yml config/outgoing_mail.yml

RUN mkdir -p log tmp/pids public/assets public/stylesheets/compiled \
    && touch Gemmfile.lock

RUN mkdir /opt/canvas/canvas-lms/vendor \
	&& cd /opt/canvas/canvas-lms/vendor \
	&& git clone https://github.com/instructure/QTIMigrationTool.git QTIMigrationTool \
	&& chmod +x QTIMigrationTool/migrate.py \
	&& cd /opt/canvas/canvas-lms

LABEL rebuild=17
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY domain.yml.tmpl /opt/canvas/canvas-lms/config/domain.yml.tmpl
COPY dbinit.sh /opt/canvas/dbinit.sh
COPY start.sh /opt/canvas/start.sh
COPY ope.rake lib/tasks/ope.rake
RUN chmod 755 /opt/canvas/*.sh	

# Make sure the line feeds are converted to nix format
RUN dos2unix /opt/canvas/*.sh

# Make sure this runs during build, will also run at at startup later
#ENV CANVAS_BUILD_CONCURRENCY=1
RUN cd /opt/canvas/canvas-lms \
	&& $GEM_HOME/bin/bundle exec rake canvas:compile_assets

RUN chown -R canvasuser:canvasuser /opt/canvas \
	&& mkdir /tmp/attachment_fu \
	&& chown -R canvasuser:canvasuser /tmp/attachment_fu

VOLUME ["/opt/canvas/canvas-lms/tmp", "/opt/canvas/canvas-lms/log"]
EXPOSE 3000

CMD ["/opt/canvas/start.sh"]






