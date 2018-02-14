#!/bin/bash
set -e

if [ -f /usr/src/app/log/app_init ]; then
    rm /usr/src/app/log/app_init
fi
if [ -f /usr/src/app/log/app_starting ]; then
    rm /usr/src/app/log/app_starting
fi

touch /usr/src/app/log/app_init

APP_DIR=/usr/src/app

# Make sure tmp folder exists
mkdir /tmp/attachement_fu

# Make sure the initial database is setup for canvas
export PGPASSWORD=$IT_PW;

# Make sure the database has a chance to come online
db_online=0
until [ $db_online -eq 1 ]
do
	echo "--> waiting for database..."
	sleep 1
	db_online=1  # Gets set back to 0 if the db connection fails
	psql -U postgres -h postgresql -tc "select 1" | grep -q 1 || db_online=0
done


#createuser --superuser canvas
echo "--> setting up user account for canvas db connection..."
psql -U postgres -h postgresql -tc "select 1 from pg_database where datname='canvas_$RAILS_ENV'" | grep -q 1 || createdb -U postgres -h postgresql -E UTF-8 -T template0 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --owner postgres canvas_$RAILS_ENV
psql -U postgres -h postgresql -tc "select 1 from pg_database where datname='canvas_queue'" | grep -q 1 || createdb -U postgres -h postgresql -E UTF-8 -T template0 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --owner postgres canvas_queue

# Make sure canvas is init
export CANVAS_LMS_ADMIN_EMAIL=$ADMIN_EMAIL
export CANVAS_LMS_ADMIN_PASSWORD=$IT_PW
export CANVAS_LMS_ACCOUNT_NAME=$LMS_ACCOUNT_NAME
export CANVAS_LMS_STATS_COLLECTION="opt_out"

cd $APP_DIR

echo "--> adjusting config files..."
cp config/outgoing_mail.yml.tmpl config/outgoing_mail.yml
sed -i "s/EMAIL_DELIVERY_METHOD/${EMAIL_DELIVERY_METHOD}/" config/outgoing_mail.yml
sed -i "s/SMTP_ADDRESS/${SMTP_ADDRESS}/" config/outgoing_mail.yml
sed -i "s/SMTP_PORT/${SMTP_PORT}/" config/outgoing_mail.yml
sed -i "s/SMTP_USER/${SMTP_USER}/" config/outgoing_mail.yml
sed -i "s/SMTP_PASS/${SMTP_PASS}/" config/outgoing_mail.yml
sed -i "s/OUTGOING_ADDRESS/${ADMIN_EMAIL}/" config/outgoing_mail.yml

cp config/domain.yml.tmpl config/domain.yml
sed -i -- "s/<VIRTUAL_HOST>/$VIRTUAL_HOST/g" config/domain.yml
cp config/database.yml.tmpl config/database.yml
sed -i -- "s/<IT_PW>/$IT_PW/g" config/database.yml

cp config/security.yml.tmpl config/security.yml
sed -i -- "s/<CANVAS_SECRET>/$CANVAS_SECRET/g" config/security.yml


# Javascript - uses float to store ints, so max is 53 bits instead of 64?
# 9_223_372_036_854_775_807 - Normal Max 64 bit int - for every language but JScript
# 0_009_007_199_254_740_991 - Max safe int for jscript (jscript, you suck in so many ways)
# 0_00*_000_000_000_000_000 - We push DB shards to this digit (0-9 shards possible)
# 0_000_***_***_000_000_000 - Auto set School Range based on time of initial startup (rolls over after 2 years)
# 0_000_000_000_***_***_*** - Leaves 1 bil ids for local tables and doesn't loose data due to jscript

# Modify ruby/gems to push database shard id out so we can use that range for school ids
# School ids are calculated in ope.rake startup and applied to database tables

# Change the shard ID so that we can use that space to sync servers
echo "--> changing id range in shard_internal.rb..."
sed -i -- "s/10_000_000_000_000/1_000_000_000_000_000/g" $GEM_HOME/gems/switchman-*/app/models/switchman/shard_internal.rb

# Need to adjust the partitions values for version tables - tables aren't created when they should be with very large ids
sed -i -- "s/5_000_000/1_000_000_000_000_000/g" $APP_DIR/config/initializers/simply_versioned.rb
# Constraint gets altered during ope:startup



# This will change, make sure to deal with it
# NOTE: moved to ope.rake -> startup
#echo "--> resetting encryption key hash..."
#$GEM_HOME/bin/bundle exec rake db:reset_encryption_key_hash

# Generate the initial db if a table called versions doesn't already exist
# NOTE: moved to ope.rake -> startup
#count=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tqc "select count(tablename) as count from pg_tables where tablename='versions'"`
#psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tc "select 1 from pg_tables where tablename='versions'" | grep -q 1 || $GEM_HOME/bin/bundle exec rake db:initial_setup
#if [ $count != '1' ]; then
#    # Run initial setup
#    echo "--> Running initial db setup..."
#    $GEM_HOME/bin/bundle exec rake db:initial_setup
#    #$GEM_HOME/bin/bundle exec rake canvas:compile_assets
#fi

# Make sure brand configs are present
#$GEM_HOME/bin/bundle exec rake brand_configs:generate_and_upload_all
# Rake::Task['brand_configs:generate_and_upload_all'].invoke

# Setup auditing, sequence range, db migrate and compile assets if needed
echo "--> Running ope:startup..."
$GEM_HOME/bin/bundle exec rake ope:startup --trace


# This is run by supervisord 
#$GEM_HOME/bin/bundle exec rails server

# Adding dev key?
#psql -U canvas -d canvas_development -c "INSERT INTO developer_keys (api_key, email, name, redirect_uri) VALUES ('test_developer_key', 'canvas@example.edu', 'Canvas Docker', 'http://localhost:8000');"

# 'crypted_token' value is hmac sha1 of 'canvas-docker' using default config/security.yml encryption_key value as secret
#psql -U canvas -d canvas_development -c "INSERT INTO access_tokens (created_at, crypted_token, developer_key_id, purpose, token_hint, updated_at, user_id) SELECT now(), '4bb5b288bb301d3d4a691ebff686fc67ad49daa8', dk.id, 'canvas-docker', '', now(), 1 FROM developer_keys dk where dk.email = 'canvas@example.edu';"


# Make sure this is all owned by the correct user
#echo "setting permissions..."
#chown -R docker:docker $APP_DIR

rm -f /usr/src/app/log/app_init
touch /usr/src/app/log/app_starting

echo "-----> launching supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf