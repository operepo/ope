#!/bin/sh

# Recreate admin user with current admin password
echo "from django.contrib.auth.models import User; \
User.objects.filter(username='admin').delete(); \
User.objects.create_superuser('admin', 'admin@correctionsed.com', '$IT_PW')" | kalite shell
#python manage.py shell

# Command to pull en language pack?
if [ ! -f /root/.kalite/locale/en/en_metadata.json ]; then
    kalite manage retrievecontentpack download en
fi
# Command to scan content for videos?
kalite manage videoscan

# Run kalite
kalite start --foreground
