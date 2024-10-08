FROM debian:jessie
#FROM debian:stretch
LABEL rebuild=22
# ope-fog - Fogproject.org - System imaging server
# Build with docker build -t ope-fog .

#INSTRUCTIONS
# Build the fog container and run it with the docker-compose command
# Download OPE system images


# To copy to offline server use the setup tool

MAINTAINER Ray Pulsipher <ray@cmagic.biz>
LABEL Description="Fogproject server Image for Open Prison Education" Vendor="openprisoneducation.com" Version="0.1"

#RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
#ENV LANG=C.UTF-8
ENV TERM=xterm
ENV LC_TYPE en_US.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

LABEL REBULID=13
#RUN echo "deb http://ftp.us.debian.org/debian jessie-backports main" >> /etc/apt/sources.list \
RUN apt-get update \
&& apt-get -y upgrade \
&& apt-get install -y wget net-tools nano python-pip python-dev libmysqlclient-dev git \
apache2 bc build-essential cpp curl g++ gawk gcc gzip htmldoc lftp libapache2-mod-php5 libc6 libcurl3 \
m4 mysql-client mysql-server net-tools nfs-kernel-server openssh-server php5 php5-cli php5-curl php5-fpm \ 
php5-gd php5-json php5-mcrypt php5-mysqlnd php-gettext sysv-rc-conf tar tftpd-hpa tftp-hpa \
unzip vsftpd wget xinetd zlib1g dos2unix supervisor iptables syslinux nfs-kernel-server netbase locales \
kmod genisoimage isolinux liblzma-dev \
&& pip install MySQL-python \
&& apt-get clean \
&& /usr/bin/mysql_install_db
# pimd?? Need to get multicast working?

#RUN apt-get install -y wget nano python-pip python-dev git \
#apache2 bc build-essential cpp curl g++ gawk gcc genisoimage gzip \ 
#htmldoc isolinux lftp libapache2-mod-php7.0 libc6 libcurl3 liblzma-dev \
#m4 mysql-client mysql-server net-tools nfs-kernel-server openssh-server \ 
#php7.0 php7.0-bcmath php7.0-cli php7.0-curl php7.0-fpm php7.0-gd \
#php7.0-json php7.0-mbstring php7.0-mcrypt php7.0-mysql php7.0-mysqlnd \
#php-gettext sysv-rc-conf tar tftpd-hpa tftp-hpa unzip vsftpd wget xinetd \
#zlib1g dos2unix supervisor iptables syslinux nfs-kernel-server netbase locales \
#kmod


#RUN apt-get install -y python-mysql.connector

# Enable php-fpm
#RUN a2enmod proxy_fcgi setenvif && \
#a2enconf php7.0-fpm

# RUN dpkg-reconfigure locales
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    dpkg-reconfigure locales && \
    /usr/sbin/update-locale LANG=en_US.UTF-8
ENV LC_ALL en_US.UTF-8


# Get pipework
COPY pipework /bin/pipework
RUN chmod +x /bin/pipework
#RUN wget --no-check-certificate -nv https://raw.github.com/jpetazzo/pipework/master/pipework \
#    && chmod +x pipework


LABEL REBUILD = 6
# Load up our settings - will start things with 127.0.0.1 as the ip
RUN mkdir -p /opt/fog
COPY .fogsettings /opt/fog
RUN cp /opt/fog/.fogsettings /

# Pull current build from GIT
RUN git clone https://github.com/FOGProject/fogproject.git /fog_src; \
cd /fog_src; \
git checkout dev-branch; \
git pull origin dev-branch;

# Copy in the project certs
COPY snapins/ssl/* /opt/fog/snapins/ssl/
COPY other/ssl/* /var/www/fog/management/other/ssl/

# Do the install for fog to pull packages (touch mysql files to force
# copyup operation https://github.com/docker/for-linux/issues/72)
RUN cd /fog_src/bin/ \
&& find /var/lib/mysql -exec touch -c -a {} + \
&& ./installfog.sh -y

LABEL rebuild=63
RUN mkdir -p /etc/nginx/conf.d
COPY nginx.tmpl /nginx.tmpl
# exit 0 at the end to ignore error if this file doesn't exist
RUN rm /etc/apache2/sites-enabled/000-default.conf; exit 0

#COPY 001-fog.conf /001-fog.conf.orig 
#COPY 001-fog.conf /etc/apache2/sites-enabled/001-fog.conf
#COPY ports.conf /ports.conf
#COPY ports.conf /etc/apache2/ports.conf

# Copy in the startup scripts
COPY update_fog_ip.py /fog_src/bin/
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY start.sh /start.sh
COPY tftpd-hpa /etc/default/tftpd-hpa
COPY nfs-static-ports.conf /etc/sysctl.d/nfs-static-ports.conf
COPY nfs-kernel-server /etc/default/nfs-kernel-server
COPY nfs-common /etc/default/nfs-common
COPY index.html /var/www/html/index.html
COPY vsftpd.conf /etc/vsftpd.conf
COPY update_password.sh /fog_src/bin/

# Setup permissions and ownership as needed
# NOTE - user fog became fogproject
RUN chmod +x /start.sh \
    && chmod 644 /etc/default/tftpd-hpa \
    && chmod +x /fog_src/bin/update_fog_ip.py \
    && dos2unix /start.sh /etc/default/tftpd-hpa /fog_src/bin/update_fog_ip.py \
    && chown -R www-data:www-data /var/www/fog/management/other/ssl \
    && chown -R fogproject:www-data /opt/fog/snapins/ssl \
    && chmod +x /fog_src/bin/update_password.sh

# Deal with sgdisk uuid error during deploy - Will want to take this out when fixes get pulled into main code 7/15/17
#RUN wget -O /var/www/fog/service/ipxe/init.xz https://fogproject.org/inits/init.xz \
#    && wget -O /var/www/fog/service/ipxe/init_32.xz https://fogproject.org/inits/init_32.xz
COPY init.xz /var/www/fog/service/ipxe/init.xz
COPY init_32.xz /var/www/fog/service/ipxe/init_32.xz

VOLUME ["/var/lib/mysql", "/images", "/backup", "/etc/nginx/confg.d"]
EXPOSE 80 443 20 21 69/udp 7000-7030/udp 111 111/udp 2049 2049/udp 4045 4045/udp 34464 34463/udp 52764-52769/udp 52764-52768 52700-52730 9000-9005/udp 50102-50110/udp 43145/udp
CMD ["/start.sh"]

# PORTS web 80, webs 443, ftp 21, tftp 69/udp, nfs 111/tcpudp 2049/tcpudp, nfslock 4045/tcpudp
# mysql 3306 (don't expose), mountd 20048/tcpudp, cifs 139 139 445, proxy dhcp 4011, dns 53/tcpupd
# tftp xfer 7000-7020/udp 
# VOLUME ["/var/lib/mysql", "/tftpboot", "/images", "/opt/fog"]
#EXPOSE 7480 7443 212/udp 9098 21 69 69/udp 8099 2049 2049/udp 111/udp 111 4045/udp 4045 34463/udp 34463 7000-7100/udp

