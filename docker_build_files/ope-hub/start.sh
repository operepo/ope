#!/bin/bash
#set -d

# Make sure permissions are set on mounted folders
chown -R www-data:www-data /home/www-data/hub
chown -R www-data:www-data /home/www-data/git

# Make sure admin password is set
# cd /home/www-data/smc/web2py
# python -c "from gluon.main import save_password; save_password('$IT_PW',80)"
# python -c "from gluon.main import save_password; save_password('$IT_PW',443)"
# chown www-data:www-data parameters*.p*


# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

