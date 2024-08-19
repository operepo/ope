FROM python:alpine3.20

LABEL Author="Ray Pulspher <ray@cmagic.biz>"
LABEL Description="Canvas Utiliy Hub - Image for Open Prison Education"
LABEL Vendor="openprisoneducation.com"
LABEL Version="1.0"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install base
RUN apk update \
    && apk add --update --no-cache \
        bash musl musl-dev linux-headers pcre-dev coreutils build-base nasm ca-certificates curl tar \
        libc-dev openssl-dev zlib-dev yasm-dev lame-dev freetype-dev opus-dev \
        rtmpdump-dev x264-dev x265-dev xvidcore-dev libass-dev libwebp-dev \
        libvorbis-dev libogg-dev libtheora-dev libvpx-dev \
        mysql-client libxml2-dev lame-libs \
        py3-cairo py3-cairo-dev py3-cffi \
        unzip wget net-tools git git-daemon unzip \
        openssl zip postgresql-dev openldap-dev \
        supervisor libffi-dev pcre libxml2 libxslt-dev cargo \
        jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev \
        font-noto msttcorefonts-installer fontconfig nano gdk-pixbuf-dev \
    && update-ms-fonts \
    && fc-cache -f
#RUN apk add --update --no-cachce libressl-dev
# py-pip
# Make sure python3 runs under the python command
    #&& ln -s /usr/bin/python3 /usr/bin/python \
#RUN ln -s /usr/bin/python3 /usr/bin/python \
RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install --upgrade setuptools ldap3 pycryptodome requests \
        paramiko ecdsa isodate pywinrm crypto PyMySQL \
        psycopg2-binary uwsgi uwsgitop psutil redis pycanvas lz4 \ 
        webvtt-py langcodes language_data bs4 lxml openpyxl Pillow WeasyPrint uwsgitop pydantic pylti1p3 django==5.0.6
#    && python -m pip install xlrd==1.2.0 \
# pytube3 - use fix 701 for now
#pip install git+https://github.com/nficano/pytube.git@refs/pull/701/head
# matplotlib reportlab ldap pycrypto changed to pycryptodome  python-ldap changed to ldap3
# FFMPEG_VER=3.4.9
# --enable-avresample
RUN FFMPEG_VER=7.0.1 \ 
    && curl -s https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VER}.tar.gz | tar zxvf - -C . \
    && cd ffmpeg-${FFMPEG_VER} \
    && ./configure \
        --disable-debug --enable-version3 --enable-small --enable-gpl \
        --enable-nonfree --enable-postproc --enable-openssl \
        --enable-libfreetype --enable-libmp3lame \
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


COPY start.sh /start.sh
COPY supervisord.conf /etc/supervisor/supervisord.conf

WORKDIR /home/www-data/hub

RUN chmod +x /start.sh \
     && chown -R www-data:www-data $W2P_DIR \
     && chown -R git:git $INSTALL_DIR/git

ENV USER=www-data

VOLUME ["/home/www-data/git", "/home/www-data/hub" \
]

EXPOSE 8100 9418