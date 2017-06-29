FROM debian:jessie
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

ENV DEBIAN_FRONTEND=noninteractive

LABEL REBULID=13
RUN apt-get update; \
apt-get -y upgrade

RUN apt-get install -y wget net-tools nano python-pip python-dev libmysqlclient-dev git \
apache2 bc build-essential cpp curl g++ gawk gcc gzip htmldoc lftp libapache2-mod-php5 libc6 libcurl3 \
m4 mysql-client mysql-server net-tools nfs-kernel-server openssh-server php5 php5-cli php5-curl php5-fpm \ 
php5-gd php5-json php5-mcrypt php5-mysqlnd php-gettext sysv-rc-conf tar tftpd-hpa tftp-hpa \
unzip vsftpd wget xinetd zlib1g dos2unix supervisor iptables syslinux
RUN pip install MySQL-python
RUN apt-get clean

# RUN dpkg-reconfigure locales

# Get pipework
COPY pipework /bin/pipework
RUN chmod +x /bin/pipework
#RUN wget --no-check-certificate -nv https://raw.github.com/jpetazzo/pipework/master/pipework \
#    && chmod +x pipework

# Download fog server
# RUN wget -v -O fog.tar.gz   "https://downloads.sourceforge.net/project/freeghost/FOG/fog_1.3.4/fog_1.3.4.tar.gz?r=https%3A%2F%2Ffogproject.org%2F&ts=1488250317&use_mirror=cytranet"
# RUN tar -xvzf fog.tar.gz
# RUN cd /fog_1.3.4/bin \
#	&& ./installfog.sh -Y

LABEL REBUILD = 2
# Load up our settings
RUN mkdir -p /opt/fog
COPY .fogsettings /opt/fog

# Update fog settings with the current public ip
# Try initial build with 127.0.0.1
#RUN sed -i -- "s/<PUBLIC_IP>/$PUBLIC_IP/g" /opt/fog/.fogsettings

# Pull current build from GIT
RUN git clone https://github.com/FOGProject/fogproject.git /fog_src; \
cd /fog_src; \
git checkout dev-branch; \
git pull;

# Make sure our utility to update things is in place
COPY update_fog_ip.py /fog_src/bin/
RUN chmod +x /fog_src/bin/update_fog_ip.py \
    && cp /opt/fog/.fogsettings /


# Note - this will get run again on docker startup
RUN cd /fog_src/bin/; \
./installfog.sh -y

# Shutdown fog services
# TODO

# Rename images so we can map images to an external volume
# NOTE - startup script should copy images_orig on startup
RUN mv /images /images_orig; \
mkdir /images

LABEL rebuild=17
# Copy in the startup scripts
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY start.sh /start.sh
COPY tftpd-hpa /etc/default/tftpd-hpa
RUN chmod +x /start.sh \
    && chmod 644 /etc/default/tftpd-hpa \
    && dos2unix /start.sh /etc/default/tftpd-hpa

VOLUME ["/var/lib/mysql", "/images", "/backup"]
# VOLUME ["/var/lib/mysql", "/tftpboot", "/images", "/opt/fog"]
#EXPOSE 7480 7443 212/udp 9098 21 69 69/udp 8099 2049 2049/udp 111/udp 111 4045/udp 4045 34463/udp 34463 7000-7100/udp
EXPOSE 80 443 21 69/udp 7000-7020/udp
# PORTS web 80, webs 443, ftp 21, tftp 69/udp, nfs 111/tcpudp 2049/tcpudp, nfslock 4045/tcpudp
# mysql 3306 (don't expose), mountd 20048/tcpudp, cifs 139 139 445, proxy dhcp 4011, dns 53/tcpupd
# tftp xfer 7000-7020/udp 
CMD ["/start.sh"]


# Set password to ENV password

# mounts
#/var/lib/mysql - volume
#/tftpboot images
#/images
#/opt/fog/.fogsettings??
#/opt/fog/snapins/ssl/.srvprivate.key - ssl path?
