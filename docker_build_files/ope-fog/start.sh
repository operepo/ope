#!/bin/bash
set -e

# activate ICMP broadcast/multicast replise
echo 0 > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts

ip link set lo multicast on
ip link set eth0 multicast on

# Make sure the .mntcheck files exist
mkdir -p /images/dev
touch /images/.mntcheck
touch /images/dev/.mntcheck


# Start system services so nfs works
echo "Setting NFS params..."
#service mountall.sh start
/etc/init.d/rpcbind restart
/etc/init.d/nfs-common restart
/etc/init.d/nfs-kernel-server restart


# Make sure images folder is present
mkdir -p /images/dev

# Set permissions on folders
echo "Changing permissions for /images, /tftpboot..."
chown -R fog:root /images
chmod -R 777 /images
chown -R fog:root /tftpboot
chmod -R 777 /tftpboot

WLAN_IF=eth0

echo "Setting firewall rules..."
# Enable NAT features to allow tftp through - off in host mode?
iptables -t nat -A POSTROUTING -j MASQUERADE

# Rules to forward TFTP packets
iptables -A INPUT -i $WLAN_IF -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i $WLAN_IF -p udp --dport 69 -m state --state NEW -j ACCEPT

# Allow multicast traffic through
# Rules to forward multicast packets modprobe
iptables -I INPUT -m pkttype --pkt-type multicast -j ACCEPT
iptables -I INPUT -m pkttype --pkt-type broadcast -j ACCEPT
iptables -I FORWARD -m pkttype --pkt-type multicast -j ACCEPT
iptables -I OUTPUT -m pkttype --pkt-type multicast -j ACCEPT
iptables -I INPUT -p udp --dport 12345 -j ACCEPT

iptables -t mangle -A PREROUTING -d 224.0.0.0/4 -j TTL --ttl-set 32
iptables -I INPUT -d 224.0.0.0/4 -j ACCEPT
iptables -I INPUT -s 224.0.0.0/4 -j ACCEPT
iptables -I FORWARD -s 224.0.0.0/4 -d 224.0.0.0/4 -j ACCEPT
iptables -I OUTPUT  -d 224.0.0.0/4 -j ACCEPT

# Need these if in host mode
#iptables -A INPUT -p tcp --dport 7480 -j ACCEPT
#iptables -A INPUT -p tcp --dport 7443 -j ACCEPT
#iptables -A INPUT -p tcp --dport 20 -j ACCEPT
#iptables -A INPUT -p tcp --dport 21 -j ACCEPT
#iptables -A INPUT -p udp --dport 69 -j ACCEPT
#iptables -A INPUT -p tcp --dport 2049 -j ACCEPT
#iptables -A INPUT -p udp --dport 2049 -j ACCEPT
#iptables -A INPUT -p tcp --dport 111 -j ACCEPT
#iptables -A INPUT -p udp --dport 111 -j ACCEPT
#iptables -A INPUT -p udp --dport 4045 -j ACCEPT
#iptables -A INPUT -p tcp --dport 4045 -j ACCEPT
#iptables -A INPUT -p tcp --dport 34463 -j ACCEPT
#iptables -A INPUT -p udp --dport 34463 -j ACCEPT
#iptables -A INPUT -p udp --dport 9000:9008 -j ACCEPT
#iptables -A INPUT -p udp --dport 7000:7030 -j ACCEPT
#iptables -A INPUT -p udp --dport 43870 -j ACCEPT
#iptables -A INPUT -p udp --dport 52764:52769 -j ACCEPT
#iptables -A INPUT -p tcp --dport 52764:52769 -j ACCEPT
#iptables -A INPUT -p tcp --dport 52700:52730 -j ACCEPT
#iptables -A INPUT -p udp --dport 63100 -j ACCEPT



#echo "Waiting for pipework..."
#/bin/pipework --wait -i $WLAN_IF
#/bin/pipework eth0 $CONTAINERID dhclient

# Make sure mysql is setup
/usr/bin/mysql_install_db

# Copy new settings file if it doesn't exist
if [ ! -f /opt/fog/.fogsettings ];
then
    cp /.fogsettings /opt/fog/
fi

echo "Starting mysql/apache..."
service mysql restart
service apache2 start
#cp /001-fog.conf.orig /etc/apache2/sites-enabled/001-fog.conf 
#service apache2 restart
service xinetd start

# Make sure the database scheme has been init
echo "Updating fog database..."
wget --no-check-certificate -qO - --post-data="confirm&fogverified" --no-proxy http://localhost/fog/management/index.php?node=schema

# Make sure to update with the current public ip and password
echo "Updating fog ip (update_fog_ip.py)..."
cd /fog_src/bin
python update_fog_ip.py
bash update_password.sh

# Make sure services are all up and ready
#service mysql start
# Make vsftpd warning not kill startup
#cp /001-fog.conf.orig /etc/apache2/sites-enabled/001-fog.conf 
#service apache2 restart
#service rpcbind start
#service nfs-common start
#service nfs-kernel-server start

echo "Starting fog services..."
service FOGImageReplicator restart
service FOGImageSize restart
service FOGMulticastManager restart
service FOGPingHosts restart
service FOGScheduler restart
service FOGSnapinHash restart
service FOGSnapinReplicator restart
#service tftpd-hpa start  # started by xinetd
service vsftpd start || true
service pimd start

#/bin/bash -c '. /etc/apache2/envvars; rm -Rf /var/run/apache2/*; /usr/sbin/apache2 -D FOREGROUND'

# add nginx conf files so that fog virtual hosts appear
# TODO 


# Run forever so docker container doesn't quit
trap : TERM INT; sleep infinity & wait

#exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

exit;
