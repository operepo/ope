#!/bin/bash
#set -d

# Make sure permissions are set on mounted folders
chown -R www-data:www-data /home/www-data/web2py/applications/smc/cache
chown -R www-data:www-data /home/www-data/web2py/applications/smc/databases
chown -R www-data:www-data /home/www-data/web2py/applications/smc/errors
chown -R www-data:www-data /home/www-data/web2py/applications/smc/private
chown -R www-data:www-data /home/www-data/web2py/applications/smc/uploads
chown www-data:www-data /home/www-data/web2py/applications/smc/static/media

# Make sure admin password is set
cd /home/www-data/web2py
python -c "from gluon.main import save_password; save_password('$IT_PW',80)"
python -c "from gluon.main import save_password; save_password('$IT_PW',443)"


# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

