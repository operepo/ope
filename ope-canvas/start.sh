#!/bin/bash
set -e

sed -i "s/EMAIL_DELIVERY_METHOD/${EMAIL_DELIVERY_METHOD-test}/" /opt/canvas/canvas-lms/config/outgoing_mail.yml
sed -i "s/SMTP_ADDRESS/${SMTP_ADDRESS-localhost}/" /opt/canvas/canvas-lms/config/outgoing_mail.yml
sed -i "s/SMTP_PORT/${SMTP_PORT-25}/" /opt/canvas/canvas-lms/config/outgoing_mail.yml
sed -i "s/SMTP_USER/${SMTP_USER-}/" /opt/canvas/canvas-lms/config/outgoing_mail.yml
sed -i "s/SMTP_PASS/${SMTP_PASS-}/" /opt/canvas/canvas-lms/config/outgoing_mail.yml

# Use the user already setup on the psql server
#sudo -u postgres $POSTGRES_BIN/createuser --superuser canvas
#sudo -u postgres $POSTGRES_BIN/createdb -E UTF-8 -T template0 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --owner canvas canvas_$RAILS_ENV
#sudo -u postgres $POSTGRES_BIN/createdb -E UTF-8 -T template0 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --owner canvas canvas_queue_$RAILS_ENV

export CANVAS_LMS_ADMIN_EMAIL=$ADMIN_EMAIL
export CANVAS_LMS_ADMIN_PASSWORD=$IT_PW
export CANVAS_LMS_ACCOUNT_NAME=$LMS_ACCOUNT_NAME
export CANVAS_LMS_STATS_COLLECTION="opt_out"

cd /opt/canvas/canvas-lms

cp config/domain.yml.tmpl config/domain.yml
sed -i -- "s/<VIRTUAL_HOST>/$VIRTUAL_HOST/g" config/domain.yml
sed -i -- "s/<IT_PW>/$IT_PW/g" config/database.yml

# TODO - Add check for first run so we don't have to do this each startup
$GEM_HOME/bin/bundle exec rake db:initial_setup

$GEM_HOME/bin/bundle exec rake canvas:compile_assets

$GEM_HOME/bin/bundle exec rake db:migrate

# This is run by supervisord 
#$GEM_HOME/bin/bundle exec rails server

# Adding dev key?
#psql -U canvas -d canvas_development -c "INSERT INTO developer_keys (api_key, email, name, redirect_uri) VALUES ('test_developer_key', 'canvas@example.edu', 'Canvas Docker', 'http://localhost:8000');"

# 'crypted_token' value is hmac sha1 of 'canvas-docker' using default config/security.yml encryption_key value as secret
#psql -U canvas -d canvas_development -c "INSERT INTO access_tokens (created_at, crypted_token, developer_key_id, purpose, token_hint, updated_at, user_id) SELECT now(), '4bb5b288bb301d3d4a691ebff686fc67ad49daa8', dk.id, 'canvas-docker', '', now(), 1 FROM developer_keys dk where dk.email = 'canvas@example.edu';"

# Make sure this is all owned by the correct user
chown -R canvasuser:canvasuser /opt/canvas/canvas-lms

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf