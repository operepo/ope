#!/bin/bash
set -e

re_quote() {
        sed 's/[\/&]/\\&/g' <<< "$*"
}

echo "=== RUNNING start.sh ==="

APP_DIR=/usr/src/rce

cd $APP_DIR

echo "=== Applying config settings ==="

# NOTE: Added new env variable so default domain is provided
DEFAULT_HOST="$CANVAS_RCE_DEFAULT_DOMAIN"


#echo "=== Launching supervisord ==="
#exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf


npm run start
