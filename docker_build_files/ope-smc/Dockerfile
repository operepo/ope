FROM alpine:3.13
MAINTAINER Ray Pulspher <ray@cmagic.biz>
LABEL Author="Ray Pulspher <ray@cmagic.biz>"
LABEL Description="Student Management Console - Image for Open Prison Education"
LABEL Vendor="openprisoneducation.com"
LABEL Version="1.4"

# install base
RUN apk update \
    && apk add --update --no-cache \
        bash musl musl-dev linux-headers pcre-dev coreutils build-base nasm ca-certificates curl tar \
        libc-dev openssl-dev zlib-dev yasm-dev lame-dev freetype-dev opus-dev \
        rtmpdump-dev x264-dev x265-dev xvidcore-dev libass-dev libwebp-dev \
        libvorbis-dev libogg-dev libtheora-dev libvpx-dev \
        python3 python3-dev py3-pip mysql-client libxml2-dev \
        py3-cairo py3-cairo-dev py3-cffi \
        unzip wget net-tools git git-daemon unzip \
        openssl zip postgresql-dev openldap-dev \
        supervisor libffi-dev pcre  libxml2 libxslt-dev cargo \
        jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev \
        libressl-dev font-noto msttcorefonts-installer fontconfig \
    && update-ms-fonts \
    && fc-cache -f \
# py-pip
# Make sure python3 runs under the python command
    && ln -s /usr/bin/python3 /usr/bin/python \
    && python -m pip install --upgrade pip \
    && python -m pip install --upgrade setuptools ldap3 pycryptodome requests \
        paramiko ecdsa isodate pywinrm crypto PyMySQL \
        psycopg2-binary uwsgi uwsgitop psutil redis pycanvas lz4 \ 
        webvtt-py langcodes language_data bs4 lxml openpyxl Pillow WeasyPrint uwsgitop \
#    && python -m pip install xlrd==1.2.0 \
# pytube3 - use fix 701 for now
#pip install git+https://github.com/nficano/pytube.git@refs/pull/701/head
# matplotlib reportlab ldap pycrypto changed to pycryptodome  python-ldap changed to ldap3
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
        python3-dev \
    && apk add --no-cache \
        zlib lame freetype faac opus xvidcore libass libwebp libvorbis libogg \
        libtheora libvpx \
    && rm -rf /var/cache/apk/* \
    && echo "FFMPEG Build complete"

# TEMP FIX FOR PYTUBE3
#RUN pip install git+https://github.com/nficano/pytube.git@refs/pull/701/head
# Install 9.7.0
#RUN pip install git+https://github.com/nficano/pytube.git@refs/tags/v9.7.0
LABEL pytube_version=12.1.0
RUN python -m pip install --upgrade pytube

# Set ENV Vars
ENV IT_PW changeme
ENV OFFICE_PW changeme
ENV INSTALL_DIR /home/www-data
ENV W2P_DIR $INSTALL_DIR/smc
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

# NOTE - web2py is not included in the SMC code
#LABEL rebuild_web2py=1
#
#RUN git clone --recursive https://github.com/web2py/web2py.git . \
#      && mv handlers/wsgihandler.py ./wsgihandler.py \
#      && cd gluon/packages/dal \
#      && git checkout master \
#      && cd ../../.. \
#      && python -c "from gluon.main import save_password; save_password('$IT_PW', 80)" \
#      && python -c "from gluon.main import save_password; save_password('$IT_PW', 443)"

#LABEL rebuild_smc=7
#RUN git clone https://github.com/operepo/smc.git $W2P_DIR/applications/smc \
#      && cp -f $W2P_DIR/applications/smc/routes.py $W2P_DIR/routes.py \
#      && echo '#!/bin/sh\ncd $W2P_DIR/applications/smc\npython set_admin_password.py' > /bin/set_admin_password \
#      && chmod +x /bin/set_admin_password \
#      && chmod +x $W2P_DIR/applications/smc/set_admin_password.py


# New clone smc which includes web2py already
LABEL rebuild_smc=12
#RUN git clone --depth 1 https://github.com/operepo/smc.git $W2P_DIR/ \
#      && chmod +x $W2P_DIR/web2py/applications/smc/set_admin_password.py

ENV SMC_RELEASE v1.9.83

RUN cd $W2P_DIR \
    && git init \
    && git remote add origin https://github.com/operepo/smc \
    && git fetch origin --no-tags --depth 1 refs/tags/${SMC_RELEASE}:refs/tags/${SMC_RELEASE}  \
    && git checkout ${SMC_RELEASE}

RUN cd $W2P_DIR \
    && echo "${SMC_RELEASE}" > web2py/applications/smc/app_version.txt



# Copy our files in
LABEL rebuild=24
COPY set_admin_password /bin/set_admin_password
COPY start.sh /start.sh
COPY supervisord.conf /etc/supervisor/supervisord.conf
# In smc now
#COPY ViewerJS $W2P_DIR/web2py/applications/smc/static/

# TEMP - Need this 4/30/19 - fix pytube error in current version
# shouldn't need now
# patched pytube in smc modules now
# COPY extract.py /usr/lib/python2.7/site-packages/pytube/extract.py


RUN chmod +x /start.sh \
     && chown -R www-data:www-data $W2P_DIR \
     && chown -R git:git $INSTALL_DIR/git \
     && chmod +x /bin/set_admin_password

ENV USER=www-data

VOLUME ["/home/www-data/git", "/home/www-data/smc/web2py/applications/smc/cache", \
 "/home/www-data/smc/web2py/applications/smc/databases", \
 "/home/www-data/smc/web2py/applications/smc/errors", \
 "/home/www-data/smc/web2py/applications/smc/private", \
 "/home/www-data/smc/web2py/applications/smc/static/media", \
 "/home/www-data/smc/web2py/applications/smc/uploads", \
 "/home/www-data/smc/web2py/applications/smc/sessions", \
 "/home/www-data/smc/web2py/applications/data_sync/static/blocks" \
 ]

EXPOSE 8000 9418

ENTRYPOINT ["/start.sh"]
