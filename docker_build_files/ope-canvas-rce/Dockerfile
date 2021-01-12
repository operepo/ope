FROM instructure/node-passenger:10


LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.0"

USER root

LABEL rebuild=7

# COPY supervisord.conf /etc/supervisor/supervisord.conf


# Pull the RCE server
ENV RCE_APP_HOME /usr/src/rce/
WORKDIR $RCE_APP_HOME
ENV RCE_RELEASE master
RUN mkdir -p ${RCE_APP_HOME} \
    && cd ${RCE_APP_HOME} \
    && git init \
    && git remote add origin https://github.com/instructure/canvas-rce-api \
    && git fetch origin master --no-tags --depth 1 \
    && git checkout master \
    #&& git fetch origin --no-tags --depth 1 refs/tags/${RCE_RELEASE}:refs/tags/${RCE_RELEASE} \
    #&& git checkout ${RCE_RELEASE} \
    && npm install --production \
    && echo Checkout done.

LABEL rebuild=13
COPY start.sh /usr/src/start.sh


RUN echo "Settings file permissions..." \
    && chmod 755 /usr/src/*.sh \
#    && dos2unix /usr/src/*.sh \
    && chown -R docker:docker /usr/src/*.sh /usr/src/rce

    
# Stay root at the end - supervisor will switch back to docker user
# VOLUME ["/usr/src/app/tmp", "/usr/src/app/log", "/tmp"]
EXPOSE 3010

CMD ["/usr/src/start.sh"]
