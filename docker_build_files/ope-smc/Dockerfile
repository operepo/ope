FROM alpine:3.4
MAINTAINER Ray Pulspher <ray@cmagic.biz>
LABEL Description="Student Management Console - Image for Open Prison Education"
LABEL Vendor="openprisoneducation.com"
LABEL Version="0.6"

# install base
RUN apk update \
    && apk add --update --no-cache \
        bash musl linux-headers pcre-dev coreutils build-base nasm ca-certificates curl tar \
        openssl-dev zlib-dev yasm-dev lame-dev freetype-dev opus-dev \
        rtmpdump-dev x264-dev x265-dev xvidcore-dev libass-dev libwebp-dev \
        libvorbis-dev libogg-dev libtheora-dev libvpx-dev \
        python python-dev mysql-client libxml2-dev py-pip \
        unzip wget net-tools git git-daemon unzip \
        openssl zip postgresql-dev openldap-dev \
        supervisor libffi-dev \
    && pip install --upgrade pip \
    && pip install --upgrade setuptools python-ldap pycrypto crypto PyMySQL psycopg2-binary uwsgi uwsgitop psutil \
# matplotlib reportlab ldap
    && FFMPEG_VER=3.4.2 \ 
    && curl -s http://ffmpeg.org/releases/ffmpeg-${FFMPEG_VER}.tar.gz | tar zxvf - -C . \
    && cd ffmpeg-${FFMPEG_VER} \
    && ./configure \
        --disable-debug --enable-version3 --enable-small --enable-gpl \
        --enable-nonfree --enable-postproc --enable-openssl \
        --enable-avresample --enable-libfreetype --enable-libmp3lame \
        --enable-libx264 --enable-libx265 --enable-libopus --enable-libass \
        --enable-libwebp --enable-librtmp --enable-libtheora \
        --enable-libvorbis --enable-libvpx --enable-libxvid \
    && make -j"$(nproc)" install \
    && cd .. \
    && rm -rf ffmpeg-${FFMPEG_VER} \
    && apk del --purge \
        musl-dev linux-headers pcre-dev coreutils build-base nasm curl tar openssl-dev zlib-dev yasm-dev \
        lame-dev freetype-dev opus-dev xvidcore-dev libass-dev libwebp-dev \
        libvorbis-dev libogg-dev libtheora-dev libvpx-dev \
        python-dev \
    && apk add --no-cache \
        zlib lame freetype faac opus xvidcore libass libwebp libvorbis libogg \
        libtheora libvpx \
    && rm -rf /var/cache/apk/* \
    && echo "FFMPEG Build complete"

# Set ENV Vars
ENV IT_PW changeme
ENV OFFICE_PW changeme
ENV INSTALL_DIR /home/www-data
ENV W2P_DIR $INSTALL_DIR/web2py
#ENV TEMP=xterm

WORKDIR $INSTALL_DIR

USER root

RUN mkdir $W2P_DIR \
    && mkdir $INSTALL_DIR/git

# Setup users
RUN addgroup www-data \
      && adduser -D -H -s /bin/bash git \
      && adduser -D -s /bin/bash -G www-data www-data


WORKDIR $W2P_DIR

LABEL rebuild_web2py=1

RUN git clone --recursive https://github.com/web2py/web2py.git . \
      && mv handlers/wsgihandler.py ./wsgihandler.py \
      && cd gluon/packages/dal \
      && git checkout master \
      && cd ../../.. \
      && python -c "from gluon.main import save_password; save_password('$IT_PW', 80)" \
      && python -c "from gluon.main import save_password; save_password('$IT_PW', 443)"

LABEL rebuild_smc=7
RUN git clone https://github.com/operepo/smc.git $W2P_DIR/applications/smc \
      && cp -f $W2P_DIR/applications/smc/routes.py $W2P_DIR/routes.py \
      && echo '#!/bin/sh\ncd $W2P_DIR/applications/smc\npython set_admin_password.py' > /bin/set_admin_password \
      && chmod +x /bin/set_admin_password \
      && chmod +x $W2P_DIR/applications/smc/set_admin_password.py

# Copy our files in
LABEL rebuild=16
COPY start.sh /start.sh
COPY supervisord.conf /etc/supervisor/supervisord.conf

COPY ViewerJS $W2P_DIR/applications/smc/static/

RUN chmod +x /start.sh \
     && chown -R www-data:www-data $W2P_DIR \
     && chown -R git:git $INSTALL_DIR/git

ENV USER=www-data

VOLUME ["/home/www-data/git", "/home/www-data/web2py/applications/smc/cache", "/home/www-data/web2py/applications/smc/databases", "/home/www-data/web2py/applications/smc/errors", "/home/www-data/web2py/applications/smc/private", "/home/www-data/web2py/applications/smc/static/media", "/home/www-data/web2py/applications/smc/uploads"]

EXPOSE 8000 9418

ENTRYPOINT ["/start.sh"]
