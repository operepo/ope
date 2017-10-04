#!/bin/bash

. /etc/apache2/envvars
chown -R www-data:www-data /home/www-data
rm -Rf /var/run/apache2/*
/usr/sbin/apache2 -D FOREGROUND

