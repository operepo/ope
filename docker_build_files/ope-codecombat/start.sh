#!/bin/bash
set -e

# Clear done indicator until we see if we need to download new dump file
rm /home/coco/codecombat/data/.dl_complete

# Give mongo a chance to initialize
echo "Waiting for mongo to startup..."
while ! /usr/bin/mongo --eval "db.version()" > /dev/null 2>&1; do sleep 0.1; done
#sleep 20

cd /home/coco/codecombat/data


# Make sure we have downloaded the dump.tar.gz file
if [ ! -f /home/coco/codecombat/data/dump.tar.gz ]
then
	echo "Pulling coco database..."
	# make sure we mark that we will need to import
	rm /home/coco/codecombat/data/.unpacked
	rm /home/coco/codecombat/data/.db_updated
	# Pull the database dump and unpack it
	wget -O dump.tar.gz.tmp http://analytics.codecombat.com:8080/dump.tar.gz
	# If it is too small, don't bother unpacking it - we are offline
	SIZE=`ls -l dump.tar.tz.tmp | awk '{print $5}'`
	if [ $SIZE -gt  100000000 ]
	then
		rm dump.tar.gz
		mv dump.tar.gz.tmp dump.tar.gz
		# Unpack the database
		tar xzf dump.tar.gz
		# Signal that the data is unpacked and ready
		touch /home/coco/codecombat/data/.unpacked
	else
		echo "Invalid size, assuming offline mode"
	fi
fi
# Signal that the dl is complete so that the sync app can pull a copy to the usb drive
touch /home/coco/codecombat/data/.dl_complete

# See if we need to import the db
if [ -f /home/coco/codecombat/data/.db_updated ]
then
	echo "Database import already done - remove codecombat/data/.db_updated and codecombat/data/dump.tar.gz to update database"
else
	# Wait until the dump file is available and unpacked
	while [ ! -f /home/coco/codecombat/data/.unpacked ]
	do
		echo "Waiting for dump.tar.gz to become available and unpacked"
		sleep 10
	done

	#/home/coco/codecombat/bin/coco-mongodb &
	#mongorestore --drop --host 127.0.0.1
	echo "Importing coco database..."
	#/home/coco/codecombat/bin/coco-pull-test-db
	# Shutdown so it can start up under supervisord
	#/usr/bin/mongod --quiet --config /etc/mongod.conf --shutdown
	#/home/coco/codecombat/bin/coco-mongodb --shutdown
	
	#cd dump
	mongoexport --db coco --collection users --out ./users.json
	mongorestore --drop --batchSize 100 ./dump
	mongoimport --db coco --upsert -c users ./users.json
	#cat  ./users.json
	#rm -r dump
	touch /home/coco/codecombat/data/.db_updated

fi	

# Make sure this is all owned by the correct user
#chown -R coco:coco /home/coco

cd /home/coco/codecombat
# Turn on the npm server
exec npm run dev
#exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf