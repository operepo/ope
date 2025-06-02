#!/bin/sh

# Download the ClamAV files so that this can be a private mirror server

# These should show up in the volume and be easily synced to the offline network

# See if we are online
MINSIZE="50000"

echo "Pulling clamav virus patterns..."

FNAME="bytecode.cvd"
TMP=`wget -S --spider http://database.clamav.net/$FNAME 2>&1| grep 'Content-Length' | awk '{print $2}'`
if [ $TMP -gt $MINSIZE ]; then
	wget -O /usr/share/nginx/html/$FNAME http://database.clamav.net/$FNAME
else
	echo "Unable to get $FNAME"
fi

FNAME="daily.cvd"
TMP=`wget -S --spider http://database.clamav.net/$FNAME 2>&1| grep 'Content-Length' | awk '{print $2}'`
if [ $TMP -gt $MINSIZE ]; then
	wget -O /usr/share/nginx/html/$FNAME http://database.clamav.net/$FNAME
else
	echo "Unable to get $FNAME"
fi

FNAME="main.cvd"
TMP=`wget -S --spider http://database.clamav.net/$FNAME 2>&1| grep 'Content-Length' | awk '{print $2}'`
if [ $TMP -gt $MINSIZE ]; then
	wget -O /usr/share/nginx/html/$FNAME http://database.clamav.net/$FNAME
else
	echo "Unable to get $FNAME"
fi

echo "Done!"
