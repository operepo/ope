#!/bin/bash

##if [ ! -f /var/www/data/admin.sqlite ];
##then
	##echo "grabbing rachel"
	##cd /var/www/html
	##git clone https://github.com/rachelproject/contentshell.git .
	

##fi

php /reset_pw.php
bash -c '. /etc/apache2/envvars ; chown -R www-data:www-data /var/www/html; /usr/sbin/apache2 -D FOREGROUND'

