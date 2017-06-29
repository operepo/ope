#!/bin/bash
set -e

# Set permissions on folders
chown -R fog:root /images
chmod -R 770 /images

# Enable NAT features to allow tftp through
iptables -t nat -A POSTROUTING -j MASQUERADE

echo "Waiting for pipework..."
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



cd /fog_src/bin
# Make sure to update with the current public ip
python update_fog_ip.py

# Make sure services are all up and ready
service mysql start
service tftpd-hpa start
#service vsftpd start
service xinetd start
service apache2 start

service FOGImageReplicator start
service FOGImageSize start
service FOGMulticastManager start
service FOGPingHosts start
service FOGScheduler start
service FOGSnapinHash start
service FOGSnapinReplicator start


#/bin/bash -c '. /etc/apache2/envvars; rm -Rf /var/run/apache2/*; /usr/sbin/apache2 -D FOREGROUND'

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

exit;
