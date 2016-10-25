FROM ubuntu:16.04
# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .

#TODO - Auto disable student collaboration features

#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.

# To copy to offline server use the setup tool

ENV LANG=C.UTF-8
ENV TERM=xterm

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Canvas LMS by Instructure - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"


ENV RAILS_ENV production
ENV GEM_HOME /opt/canvas/.gems

# add nodejs and recommended ruby repos
RUN apt-get update \
    && apt-get -y install curl software-properties-common nano \
    && add-apt-repository -y ppa:brightbox/ruby-ng \
    && apt-get update \
    && apt-get install -y ruby2.1 ruby2.1-dev supervisor \
        zlib1g-dev libxml2-dev libxslt1-dev libsqlite3-dev postgresql-client libpq5 libpq-dev libxmlsec1-dev curl make g++ git

RUN curl -sL https://deb.nodesource.com/setup_6.x | bash \
    && apt-get install -y nodejs

RUN apt-get clean && rm -Rf /var/cache/apt

# Set the locale to avoid active_model_serializers bundler install failure
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN groupadd -r canvasuser -g 433 && \
    adduser --uid 431 --system --gid 433 --home /opt/canvas canvasuser && \
    adduser canvasuser sudo && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN gem install bundler --version 1.12.5



RUN cd /opt/canvas \
    && git clone https://github.com/instructure/canvas-lms.git

WORKDIR /opt/canvas/canvas-lms


RUN for config in amazon_s3 delayed_jobs domain file_store security external_migration \
       ; do cp config/$config.yml.example config/$config.yml \
       ; done

LABEL rebuild=3

COPY database.yml config/database.yml
COPY redis.yml config/redis.yml
COPY cache_store.yml config/cache_store.yml
COPY production-local.rb config/environments/production-local.rb
COPY outgoing_mail.yml config/outgoing_mail.yml

RUN $GEM_HOME/bin/bundle install --without="mysql"

RUN npm install --unsafe-perm \
    && $GEM_HOME/bin/bundle exec rake canvas:compile_assets \
    && npm install --unsafe-perm -g coffee-script@1.6.2
	#    && sudo npm install --unsafe-perm -g coffee-script@1.6.2

RUN mkdir -p log tmp/pids public/assets public/stylesheets/compiled \
    && touch Gemmfile.lock

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY domain.yml.tmpl /opt/canvas/canvas-lms/config/domain.yml.tmpl
COPY dbinit.sh /opt/canvas/dbinit.sh
COPY start.sh /opt/canvas/start.sh
RUN chmod 755 /opt/canvas/*.sh	

RUN chown -R canvasuser: /opt/canvas

VOLUME ["/opt/canvas/canvas-lms/tmp", "/opt/canvas/canvas-lms/log"]
EXPOSE 3000

CMD ["/opt/canvas/start.sh"]






