FROM instructure/node-passenger:20


LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Canvas LMS by Instructure - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.4"

USER root

LABEL rebuild=8

# Pull the RCE server (canvas-rce-api)
# 1.27.7 isn't tagged upstream, so pin to the commit (latest master as of 2026-06).
# The node-passenger:20 base has no git - grab the source tarball with curl instead.
ENV RCE_APP_HOME=/usr/src/rce/
WORKDIR $RCE_APP_HOME
#ENV RCE_RELEASE=master
ENV RCE_RELEASE=e076fe28a09f4e41058da0983b5ef2c809123d9f
RUN mkdir -p ${RCE_APP_HOME} \
    && curl -fsSL https://github.com/instructure/canvas-rce-api/archive/${RCE_RELEASE}.tar.gz \
        | tar -xz --strip-components=1 -C ${RCE_APP_HOME} \
    # Upstream imports the devDependency "dev-null" at runtime (app/middleware/requestLogs.js),
    # so move it to dependencies and install prod deps only (instead of all devDependencies).
    && npm pkg set dependencies.dev-null=0.1.1 \
    && npm pkg delete devDependencies.dev-null \
    && npm install --omit=dev --no-audit --no-fund \
    && npm cache clean --force \
    && echo Checkout done.

LABEL rebuild=14
COPY start.sh /usr/src/start.sh
COPY packageBookmark.js /usr/src/rce/app/api/packageBookmark.js

RUN echo "Settings file permissions..." \
    && chmod 755 /usr/src/*.sh \
    && chown -R docker:docker /usr/src/*.sh /usr/src/rce


EXPOSE 3010

CMD ["/usr/src/start.sh"]
