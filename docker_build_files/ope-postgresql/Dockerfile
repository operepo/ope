# ope-postgresql - Postgresql server, used by other containers for the OPE project
# Build with docker build -t ope-postgresql .
#
# Data folders (inside the ../volumes/postgresql/data volume) are versioned by PG major version:
#   pgdata        - PG 9.6  (legacy - upgraded to 12 by the old 12.9 image)
#   pgdata-12.9   - PG 12
#   pgdata-18     - PG 18 (current)
# On first start of this image, if pgdata-12.9 exists and hasn't been converted, the entrypoint
# runs pg_upgrade (12 -> 18) using the PG12 binaries copied into /pg12 below.

# --- Stage 1: grab the PG12 binaries/libs/share files needed by pg_upgrade ---
# 12.22 is the final PG12 release. Alpine 3.21 is the newest base it was built on, so its ICU (74)
# differs from the PG18 image - copy those libs along too (kept in /pg12/icu, only used for the upgrade).
FROM postgres:12.22-alpine3.21 AS pg12
RUN set -eux; \
    mkdir -p /pg12/icu; \
    cp -a /usr/local/bin /usr/local/lib /usr/local/share /pg12/; \
    cd /pg12/bin && rm -f docker-*.sh gosu su-exec; \
    # Drop static libs and the LLVM JIT bits (JIT isn't needed to dump/upgrade and libLLVM isn't in the new image)
    rm -rf /pg12/lib/*.a /pg12/lib/pkgconfig /pg12/lib/postgresql/llvmjit* /pg12/lib/postgresql/bitcode /pg12/lib/postgresql/pgxs; \
    cp -a /usr/lib/libicudata.so.74* /usr/lib/libicuuc.so.74* /usr/lib/libicui18n.so.74* /pg12/icu/


# --- Stage 2: the actual PG18 server image ---
FROM postgres:18.6-alpine3.24

LABEL maintainer="Ray Pulsipher <ray@cmagic.biz>"
LABEL description="Postgresql container used by canvas - Image for Open Prison Education"
LABEL vendor="openprisoneducation.com"
LABEL version="1.3"


LABEL rebuild=32
# Previous major version binaries for pg_upgrade (12 -> 18)
COPY --from=pg12 /pg12 /pg12/
# Make sure the old binaries can actually run on this base (fails the build if a lib is missing)
RUN LD_LIBRARY_PATH=/pg12/icu /pg12/bin/postgres --version \
    && LD_LIBRARY_PATH=/pg12/icu /pg12/bin/pg_ctl --version

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
COPY update_pw.sh /update_pw.sh
RUN chmod +x /update_pw.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
VOLUME /var/lib/postgresql/data
EXPOSE 5432
CMD ["postgres"]
# vim:set ft=dockerfile:
