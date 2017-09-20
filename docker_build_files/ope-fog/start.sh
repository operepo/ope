#!/bin/bash
set -e

# Make sure the .mntcheck files exist
mkdir -p /images/dev
touch /images/.mntcheck
touch /images/dev/.mntcheck


# Start system services so nfs works
service mountall.sh start
/etc/init.d/rpcbind start
/etc/init.d/nfs-common start
/etc/init.d/nfs-kernel-server start


# Make sure images folder is present
mkdir -p /images/dev

# Set permissions on folders
chown -R fog:root /images
chmod -R 777 /images
chown -R fog:root /tftpboot
chmod -R 777 /tftpboot

# Enable NAT features to allow tftp through
iptables -t nat -A POSTROUTING -j MASQUERADE

#echo "Waiting for pipework..."
#/bin/pipework --wait

# Make sure mysql is setup
/usr/bin/mysql_install_db

# Copy new settings file if it doesn't exist
if [ ! -f /opt/fog/.fogsettings ];
then
    cp /.fogsettings /opt/fog/
fi

# Convert apache to use 7480 instead of 80 if running netowrk_mode: host
#sed -i "s/:80/:7480/" /etc/apache2/sites-enabled/*.conf
#sed -i "s/Listen 80/Listen 7480/" /etc/apache2/ports.conf
# Convert apache to use 7443 instead of 443
#sed -i "s/:443/:7443/" /etc/apache2/sites-enabled/*.conf
#sed -i "s/Listen 443/Listen 7443/" /etc/apache2/ports.conf

service mysql start
service apache2 start

# Make sure the database scheme has been init
wget --no-check-certificate -qO - --post-data="confirm&fogverified" --no-proxy http://localhost/fog/management/index.php?node=schema

# Make sure to update with the current public ip and password
cd /fog_src/bin
bash update_password.sh
python update_fog_ip.py

# Make sure services are all up and ready
#service mysql start
service tftpd-hpa start
# Make vsftpd warning not kill startup
service vsftpd start || true
service xinetd start
service apache2 start
#service rpcbind start
#service nfs-common start
#service nfs-kernel-server start

service FOGImageReplicator start
service FOGImageSize start
service FOGMulticastManager start
service FOGPingHosts start
service FOGScheduler start
service FOGSnapinHash start
service FOGSnapinReplicator start

#/bin/bash -c '. /etc/apache2/envvars; rm -Rf /var/run/apache2/*; /usr/sbin/apache2 -D FOREGROUND'

# Run forever so docker container doesn't quit
sleep infinity
#exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

exit;
