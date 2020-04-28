#!/bin/bash

#/bin/bash -c "envsubst < /etc/nginx/conf.d/mysite.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"

# Put in dummy html page if none exists
if [ ! -f /usr/share/nginx/html/index.html ]; then
   echo "<html><head><title>GCF Learn Free</title></head><body>Place holder - when the GCF volume finishes syncing, this will turn into the GCFLearnFree.org website...</body></html>" > /usr/share/nginx/html/index.html
fi

/bin/bash -c "exec nginx -g 'daemon off;'"
