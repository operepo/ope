FROM mysql:5.6


# ope-mysql - Mysql database server used by various containers
# Build with docker build -t ope-mysql .

#INSTRUCTIONS
# Build the container and run it with the docker-compose command
# Other containers will link to this and add their own db files and users


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="mysql offline database - Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

LABEL rebuild=1
#COPY ope.cnf /etc/mysql/mysql.conf.d/ope.cnf

VOLUME ["/var/lib/mysql"]
EXPOSE 3306
