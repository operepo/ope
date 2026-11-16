# ope-canvas-upgrade - one-time database upgrader for OPE canvas servers
# Build with docker build -t operepo/ope-canvas-upgrade:release .
#
# Canvas squashes old migrations, so a database from an older ope-canvas image can't be migrated by the
# current one. This image holds the intermediate canvas releases (ruby code + gems only, no assets) and
# steps the database through them - see upgrade.sh and ../ope-canvas/README.md.
#
# Same base as ope-canvas. Ruby 3.1 / 3.3 come from the same PPA the base uses for 3.4 and install side by
# side (/usr/bin/ruby3.1, /usr/bin/ruby3.3); each step has its own GEM_HOME.
FROM instructure/ruby-passenger:3.4-jammy

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas database upgrader for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.0"

ARG POSTGRES_CLIENT=18
ENV LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_CTYPE=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV RAILS_ENV=production

USER root

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  && add-apt-repository -y ppa:instructure/ruby \
  && add-apt-repository ppa:git-core/ppa -ny \
  && apt-get update -qq \
  && apt-get install -qqy --no-install-recommends \
       ruby3.1 ruby3.1-dev \
       ruby3.3 ruby3.3-dev \
       libxmlsec1-dev \
       libicu-dev \
       libidn11-dev \
       postgresql-client-$POSTGRES_CLIENT \
       tzdata \
       git \
       build-essential \
  && rm -rf /var/lib/apt/lists/* \
  && ruby3.1 -v && ruby3.3 -v && ruby -v

COPY build_step.sh ope_upgrade.rake /opt/ope/
RUN chmod +x /opt/ope/build_step.sh

# One layer per step - step | canvas release | ruby | CANVAS_RAILS | bundler (= "BUNDLED WITH" in its Gemfile.lock)
# Keep in sync with STEPS in upgrade.sh
# The chain was checked against every release in between (not just squash points): canvas sometimes adds a
# back-dated migration and squashes it a few releases later (e.g. 20241209133534_create_lti_assets appeared in
# 2025-03 and was squashed by 2025-06), so steps 4 and 6 are needed to pick those up.
RUN /opt/ope/build_step.sh 1 release/2024-03-13.297 3.1 7.0 2.5.6
RUN /opt/ope/build_step.sh 2 release/2024-08-28.241 3.1 7.1 2.5.10
RUN /opt/ope/build_step.sh 3 release/2025-01-29.487 3.3 7.1 2.5.10
RUN /opt/ope/build_step.sh 4 release/2025-05-07.341 3.3 7.1 2.6.7
RUN /opt/ope/build_step.sh 5 release/2025-08-13.321 3.4 7.2 2.6.7
RUN /opt/ope/build_step.sh 6 release/2025-10-22.358 3.4 7.2 2.6.7
RUN /opt/ope/build_step.sh 7 release/2026-01-28.626 3.4 8.0 2.6.7

COPY upgrade.sh /opt/ope/upgrade.sh
RUN chmod +x /opt/ope/upgrade.sh

VOLUME ["/backups"]
WORKDIR /opt/canvas-upgrade
CMD ["/opt/ope/upgrade.sh"]
