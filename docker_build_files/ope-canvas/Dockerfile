FROM instructure/canvas-lms:stable

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="0.4"

# ope-canvas - Canvas LMS System
# Build with docker build -t ope-canvas .

#TODO - Auto disable student collaboration features

#INSTRUCTIONS
# Build the canvas container and run it with the docker-compose command
# View the canvas website to set your admin password and configure.


USER root

# Install dos2unix
RUN apt-get update \
    && apt-get install -y dos2unix supervisor

ENV APP_HOME /usr/src/app/

# Make sure this runs during build, will also run at at startup later
ENV CANVAS_BUILD_CONCURRENCY=1

USER docker
RUN mkdir ${APP_HOME}/vendor \
	&& cd ${APP_HOME}/vendor \
	&& git clone https://github.com/instructure/QTIMigrationTool.git QTIMigrationTool \
	&& chmod +x QTIMigrationTool/migrate.py
    
#RUN rm -rf node_modules \
#    && rm -rf gems/**/node_modules \
#    && npm cache clean    

USER root
RUN rm -rf node_modules
RUN npm install
RUN $GEM_HOME/bin/bundle exec rake canvas:compile_assets --trace

USER docker


LABEL rebuild=20

COPY amazon_s3.yml config/amazon_s3.yml
COPY delayed_jobs.yml config/delayed_jobs.yml
COPY file_store.yml config/file_store.yml
COPY security.yml.tmpl config/security.yml.tmpl
COPY external_migration.yml config/external_migration.yml

COPY database.yml config/database.yml
COPY redis.yml config/redis.yml
COPY cache_store.yml config/cache_store.yml
COPY production-local.rb config/environments/production-local.rb
COPY outgoing_mail.yml config/outgoing_mail.yml

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY domain.yml.tmpl /usr/src/app/config/domain.yml.tmpl
COPY dbinit.sh /usr/src/dbinit.sh
COPY start.sh /usr/src/start.sh
COPY ope.rake lib/tasks/ope.rake



USER root
RUN chmod 755 /usr/src/*.sh	\
    && dos2unix /usr/src/*.sh \
    && mkdir /tmp/attachment_fu \
	&& chown -R docker:docker /tmp/attachment_fu

RUN chown -R docker:docker /usr/src/*.sh /usr/src/app/config /usr/src/app/vendor /usr/src/app/lib/tasks/ope.rake /usr/src/app/node_modules
    


# Stay root at the end - supervisor will switch back to docker user
VOLUME ["/usr/src/app/tmp", "/usr/src/app/log"]
EXPOSE 3000

CMD ["/usr/src/start.sh"]
