#!/bin/bash
set -e

# Give mongo a chance to initialize
echo "Waiting for mongo to startup..."
while ! /usr/bin/mongo --eval "db.version()" > /dev/null 2>&1; do sleep 0.1; done
#sleep 20

cd /home/coco/codecombat/data

# Download the codecombat data file if needed and import it
if [ -f /home/coco/codecombat/data/.db_updated ]
then
	echo "Database import already done - remove codecombat/data/.db_updated and codecombat/data/dump.tar.gz to update database"
else
	
	if [ ! -f /home/coco/codecombat/data/dump.tar.gz ]
	then
		echo "Pulling coco database..."
		wget -O dump.tar.gz http://analytics.codecombat.com:8080/dump.tar.gz
		tar xzf dump.tar.gz
	else
		echo "Reusing old dump.tar.gz file - delete this and .db_updated files to download a new dump file"
	fi
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