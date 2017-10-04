#!/bin/bash
#set -d

# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

