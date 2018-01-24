#!/bin/bash
#set -d

# Make sure permissions are set on mounted folders
chown -R www-data:www-data /home/www-data/web2py/applications/smc/cache
chown -R www-data:www-data /home/www-data/web2py/applications/smc/databases
chown -R www-data:www-data /home/www-data/web2py/applications/smc/errors
chown -R www-data:www-data /home/www-data/web2py/applications/smc/private
chown -R www-data:www-data /home/www-data/web2py/applications/smc/uploads


# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

