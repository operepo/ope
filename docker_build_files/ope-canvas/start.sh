#!/bin/bash
set -e

re_quote() {
        sed 's/[\/&]/\\&/g' <<< "$*"
}

BUNDLE=$GEM_HOME/bin/bundle
#BUNDLE=/usr/local/bin/bundle

echo "=== RUNNING start.sh ==="

# Make sure this is all owned by the correct user
echo "== Setting Folder Permissions =="
#chown -R docker:docker $APP_DIR
#chown -R docker:docker $APP_DIR/tmp
#chown -R docker:docker $APP_DIR/log
find $APP_DIR -not -user docker -exec chown docker:docker {} \+
chown -R docker:docker /tmp



if [ -f /usr/src/app/log/app_init ]; then
    rm /usr/src/app/log/app_init
fi
if [ -f /usr/src/app/log/app_starting ]; then
    rm /usr/src/app/log/app_starting
fi

touch /usr/src/app/log/app_init

APP_DIR=/usr/src/app

# Make sure tmp folder exists
mkdir -p /tmp/attachment_fu

# Make sure the initial database is setup for canvas
export PGPASSWORD=$IT_PW;

# Make sure the database has a chance to come online
db_online=0
until [ $db_online -eq 1 ]
do
	echo "= Waiting for ope-postgresql to come online ="
	sleep 1
	db_online=1  # Gets set back to 0 if the db connection fails
	psql -U postgres -h postgresql -tc "select 1" | grep -q 1 || db_online=0
done


#createuser --superuser canvas
echo "=== Configuring postgresql account for ope-canvas  ==="
psql -U postgres -h postgresql -tc "select 1 from pg_database where datname='canvas_$RAILS_ENV'" | grep -q 1 || createdb -U postgres -h postgresql -E UTF-8 -T template0 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --owner postgres canvas_$RAILS_ENV
psql -U postgres -h postgresql -tc "select 1 from pg_database where datname='canvas_queue'" | grep -q 1 || createdb -U postgres -h postgresql -E UTF-8 -T template0 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --owner postgres canvas_queue

# Make sure canvas is init - moved to docker-compose
#export CANVAS_LMS_ADMIN_EMAIL=$ADMIN_EMAIL
#export CANVAS_LMS_ADMIN_PASSWORD=$IT_PW
#export CANVAS_LMS_ACCOUNT_NAME=$LMS_ACCOUNT_NAME
#export CANVAS_LMS_STATS_COLLECTION="opt_out"

cd $APP_DIR

echo "=== Applying config settings ==="
cp config/outgoing_mail.yml.tmpl config/outgoing_mail.yml
sed -i "s/EMAIL_DELIVERY_METHOD/${EMAIL_DELIVERY_METHOD}/" config/outgoing_mail.yml
sed -i "s/SMTP_ADDRESS/${SMTP_ADDRESS}/" config/outgoing_mail.yml
sed -i "s/SMTP_PORT/${SMTP_PORT}/" config/outgoing_mail.yml
sed -i "s/SMTP_USER/${SMTP_USER}/" config/outgoing_mail.yml
ESC_SMTP_PASS=$(re_quote "${SMTP_PASS}")
sed -i "s/SMTP_PASS/ESC_SMTP_PASS/" config/outgoing_mail.yml
sed -i "s/OUTGOING_ADDRESS/${ADMIN_EMAIL}/" config/outgoing_mail.yml

# NOTE: Added new env variable so default domain is provided
DEFAULT_HOST="$CANVAS_DEFAULT_DOMAIN"

cp config/domain.yml.tmpl config/domain.yml
sed -i -- "s/<VIRTUAL_HOST>/$DEFAULT_HOST/g" config/domain.yml
cp config/database.yml.tmpl config/database.yml
ESC_IT_PW=$(re_quote "$IT_PW")
sed -i -- "s/<IT_PW>/$ESC_IT_PW/g" config/database.yml

cp config/security.yml.tmpl config/security.yml
sed -i -- "s/<CANVAS_SECRET>/$CANVAS_SECRET/g" config/security.yml
# Newer canvas requires a 64 char jwt_encryption_keys entry - derive a stable one from CANVAS_SECRET
CANVAS_JWT_ENCRYPTION_KEY=$(printf "%s" "ope-jwt-${CANVAS_SECRET}" | sha256sum | cut -c1-64)
sed -i -- "s/<CANVAS_JWT_ENCRYPTION_KEY>/$CANVAS_JWT_ENCRYPTION_KEY/g" config/security.yml
sed -i -- "s/<CANVAS_DEFAULT_DOMAIN>/$CANVAS_DEFAULT_DOMAIN/g" config/security.yml

cp config/dynamic_settings.yml.tmpl config/dynamic_settings.yml
sed -i -- "s/<CANVAS_ENC_SECRET>/$CANVAS_ENC_SECRET/g" config/dynamic_settings.yml
sed -i -- "s/<CANVAS_SIGN_SECRET>/$CANVAS_SIGN_SECRET/g" config/dynamic_settings.yml
sed -i -- "s/<CANVAS_RCE_DEFAULT_DOMAIN>/$CANVAS_RCE_DEFAULT_DOMAIN/g" config/dynamic_settings.yml
sed -i -- "s/<CANVAS_MATHMAN_DEFAULT_DOMAIN>/$CANVAS_MATHMAN_DEFAULT_DOMAIN/g" config/dynamic_settings.yml
sed -i -- "s/<CANVAS_DEFAULT_DOMAIN>/$CANVAS_DEFAULT_DOMAIN/g" config/dynamic_settings.yml
# NOTE: <CANVAS_JWK_KEYS> is replaced later by the ope:startup rake task

# Newer canvas reads the service secrets (RCE tokens, mathman signing) from Rails credentials, not
# dynamic_settings.yml - write config/credentials/production.yml.enc from CANVAS_ENC_SECRET / CANVAS_SIGN_SECRET
echo "=== Writing rails credentials (canvas_security service secrets) ==="
su docker -c "cd $APP_DIR && GEM_HOME=$GEM_HOME CANVAS_ENC_SECRET=\"$CANVAS_ENC_SECRET\" CANVAS_SIGN_SECRET=\"$CANVAS_SIGN_SECRET\" RAILS_ENV=$RAILS_ENV $BUNDLE exec ruby /usr/src/write_credentials.rb"

# This sets secure option on cookies
cp config/session_store.yml.tmpl config/session_store.yml


# Apply a sed patch only if the file exists - newer canvas releases squash/remove some of the patched files
# and a missing file would stop start.sh (set -e)
patch_if_exists() {  # file sed-expression
    if [ -f "$1" ]; then sed -i -- "$2" "$1"; else echo "  (skip - $1 not found)"; fi
}

# Fix ::int4[] instead of ::int8[] in app/models/assignment.rb (line 2477, issue #1238)
echo "=== Applying patch for issue #1238 ==="
patch_if_exists app/models/assignment.rb "s/\:\:int4\[\]/\:\:int8\[\]/g"


# Fix issue #1783 - DB Migrate broken -  => needs to be a : in the file
echo "=== Applying patch for issue #1783 ==="
patch_if_exists db/migrate/20200211143240_split_up_user_preferences.rb "s/n_strand => \[\"user_preference_migration\"/n_strand\: \[\"user_preference_migration\"/g"


# Javascript - uses float to store ints, so max is 53 bits instead of 64?
# 9_223_372_036_854_775_807 - Normal Max 64 bit int - for every language but JScript
# 0_009_007_199_254_740_991 - Max safe int for jscript (jscript, you suck in so many ways)
# 0_00*_000_000_000_000_000 - We push DB shards to this digit (0-9 shards possible)
# 0_000_***_***_000_000_000 - Auto set School Range based on time of initial startup (rolls over after 2 years)
# 0_000_000_000_***_***_*** - Leaves 1 bil ids for local tables and doesn't loose data due to jscript

# Modify ruby/gems to push database shard id out so we can use that range for school ids
# School ids are calculated in ope.rake startup and applied to database tables

# Change the shard ID so that we can use that space to sync servers - essentially turn shards off
echo "=== Patching id range in shard_internal.rb (shard.rb) ==="
# NOTE - changed to shard.rb
# NOTE - path changed with rails 6.1 - switchmand 3.0? instad of 2.2.3
for f in $GEM_HOME/gems/switchman-*/lib/switchman/shard.rb; do patch_if_exists "$f" "s/10_000_000_000_000/1_000_000_000_000_000/g"; done
grep -q "IDS_PER_SHARD = 1_000_000_000_000_000" $GEM_HOME/gems/switchman-*/lib/switchman/shard.rb || echo "=== WARNING - switchman shard id range NOT patched ==="
#sed -i -- "s/10_000_000_000_000/1_000_000_000_000_000/g" $GEM_HOME/gems/switchman-*/app/models/switchman/shard.rb
#sed -i -- "s/10_000_000_000_000/1_000_000_000_000_000/g" $GEM_HOME/gems/switchman-*/app/models/switchman/shard_internal.rb
#sed -i -- "s/10_000_000_000_000/1_000_000_000_000_000_000/g" $GEM_HOME/gems/switchman-*/app/models/switchman/shard_internal.rb

# Need to adjust the partitions values for version tables - tables aren't created when they should be with very large ids
# essentially turn version tables off
patch_if_exists $APP_DIR/config/initializers/simply_versioned.rb "s/5_000_000/1_000_000_000_000_000/g"
#sed -i -- "s/5_000_000/1_000_000_000_000_000_000/g" $APP_DIR/config/initializers/simply_versioned.rb
# DB Constraint gets altered during ope:startup

# FIX - database migration - has item duplicated  https://github.com/instructure/canvas-lms/issues/1806
#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_admin_users, :add_teacher_to_course)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_admin_users, :add_teacher_to_course)/g" $APP_DIR/db/migrate/20201216214616_more_granular_admin_users_permissions.rb
#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_admin_users, :remove_teacher_from_course)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_admin_users, :remove_teacher_from_course)/g" $APP_DIR/db/migrate/20201216214616_more_granular_admin_users_permissions.rb
#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_students, :add_student_to_course)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_students, :add_student_to_course)/g"  $APP_DIR/db/migrate/20210207214616_granular_student_permissions.rb
#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_students, :remove_student_from_course)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_students, :remove_student_from_course)/g"  $APP_DIR/db/migrate/20210207214616_granular_student_permissions.rb

#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_groups, :manage_groups_add)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_groups, :manage_groups_add)/g" $APP_DIR/db/migrate/20210308200204_granular_manage_groups_permissions.rb
#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_groups, :manage_groups_manage)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_groups, :manage_groups_manage)/g" $APP_DIR/db/migrate/20210308200204_granular_manage_groups_permissions.rb
#sed -i -- "s/    DataFixup::AddRoleOverridesForNewPermission.run(:manage_groups, :manage_groups_delete)/    #DataFixup::AddRoleOverridesForNewPermission.run(:manage_groups, :manage_groups_delete)/g" $APP_DIR/db/migrate/20210308200204_granular_manage_groups_permissions.rb

# FIX - messing with accounts during db:migrate causing new installs to fail:
# https://github.com/instructure/canvas-lms/issues/2035
#sed -i -- "s/DataFixup::ChangeImmersiveReaderAllowedOnToOn.run/# DataFixup::ChangeImmersiveReaderAllowedOnToOn.run/g" $APP_DIR/db/migrate/20210823222355_change_immersive_reader_allowed_on_to_on.rb
patch_if_exists $APP_DIR/lib/data_fixup/change_immersive_reader_allowed_on_to_on.rb "s/Account.root_accounts.active.where.not(id: Account.site_admin.id)/# Account.root_accounts.active.where.not(id: Account.site_admin.id)/g"

# Generate the initial db if a table called versions doesn't already exist
# NOTE: moved to ope.rake -> startup
# Canvas squashes old migrations - an existing database must already have the last squashed migration or
# db:migrate refuses to run. Check up front so the log says what to do instead of a stack trace.
# Same rule as canvas' own db/migrate/*_validate_migration_integrity.rb (versions read from that file):
# a db is too old if it has the initial migration, hasn't run this release's integrity check yet, and is
# missing the last squashed migration. (A db created by this release never records the squashed versions,
# but it has the integrity check version - so it is fine.)
VALIDATE_FILE=$(ls db/migrate/*_validate_migration_integrity.rb 2>/dev/null | head -1)
VALIDATE_VERSION=$(basename "${VALIDATE_FILE:-0_x}" | cut -d_ -f1)
CANVAS_MIN_DB_MIGRATION=$(grep -oE 'last_squashed_migration_version = "[0-9]+"' "${VALIDATE_FILE:-/dev/null}" | grep -oE '[0-9]+' || true)
has_schema=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tAc "select count(*) from pg_tables where tablename='schema_migrations'"`
if [ "$has_schema" = "1" ] && [ -n "$CANVAS_MIN_DB_MIGRATION" ]; then
    has_initial=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tAc "select count(*) from schema_migrations where version='20101210192618'"`
    has_validate=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tAc "select count(*) from schema_migrations where version='$VALIDATE_VERSION'"`
    has_min=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tAc "select count(*) from schema_migrations where version='$CANVAS_MIN_DB_MIGRATION'"`
    if [ "$has_initial" = "1" ] && [ "$has_validate" != "1" ] && [ "$has_min" != "1" ]; then
        last_mig=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tAc "select max(version) from schema_migrations where version < '30000000000000'"`
        echo "=================================================================================="
        echo "ERROR - the canvas database is too old for this ope-canvas image ($CANVAS_RELEASE)."
        echo "  Newest migration in the database: $last_mig"
        echo "  This release needs migration $CANVAS_MIN_DB_MIGRATION to already be applied."
        echo "  Enable the upgrader so it runs before canvas starts, then restart the stack:"
        echo "    touch docker_build_files/ope-canvas-upgrade/.enabled"
        echo "    python3 build_tools/rebuild_compose.py   (or your normal rebuild/up scripts)"
        echo "    docker compose up -d"
        echo "  (or run it by hand: docker compose stop ope-canvas; docker compose run --rm ope-canvas-upgrade)"
        echo "  The database has NOT been changed."
        echo "=================================================================================="
        # Wait instead of exiting right away so restart: always doesn't spin
        sleep 300
        exit 1
    fi
fi

count=`psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tqc "select count(tablename) as count from pg_tables where tablename='versions'"`
psql -d canvas_$RAILS_ENV -U postgres -h postgresql -tc "select 1 from pg_tables where tablename='versions'" | grep -q 1 || $BUNDLE exec rake db:initial_setup
if [ $count == '1' ]; then
    # Make sure the key is setup or things fail later.
    echo "=== Running db:reset_encryption_key_hash ==="
    $BUNDLE exec rake db:reset_encryption_key_hash
    #$GEM_HOME/bin/rake db:migrate
fi

#if [ $count != '1' ]; then
#    # Run initial setup
#    echo "--> Running initial db setup..."
#    $GEM_HOME/bin/bundle exec rake db:initial_setup
#    #$GEM_HOME/bin/bundle exec rake canvas:compile_assets
#fi

# Setup auditing, sequence range, db migrate and compile assets if needed
echo "=== Running ope:startup ==="
$BUNDLE exec rake ope:startup --trace

# Make sure brand configs are in place
$BUNDLE exec rake brand_configs:generate_and_upload_all

# Replace fonts.googleapis.com with local link
find . -name "*.css" -type f -exec sed -i 's/https:\/\/fonts.googleapis.com\/css/\/fonts\/css.css/g' {} \;
# May need to re-compile assets and restart the canvas server if css2 links are being asked for
find . -name "*.css" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/g' {} \;
find . -name "*.html.erb" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/g' {} \;
find . -name "*.html" -type f -exec sed -i 's/\/fonts\/css.css2/\/fonts\/css.css/g' {} \;

# Replace mathjax links to pull from the local server
find /usr/src/app/public/javascripts/ -name "*.js" -type f -exec sed -i 's/\/\/cdnjs.cloudflare.com//' {} \;
find /usr/src/app/public/dist/ -name "*.js" -type f -exec sed -i 's/\/\/cdnjs.cloudflare.com//' {} \;

# MathJax - local copies live in public/ajax/libs/mathjax/<version> (2.7.5 for older canvas, 2.7.7 for current).
# Canvas loads MathJax.js with $.ajax. Once the cdnjs host is stripped the request is same-origin, so jQuery
# fetches it with XHR + eval instead of a <script src> tag - MathJax then can't find its root folder or the
# ?config=/&locale= params and asks for /extensions/..., /jax/... from the site root.
# Force jQuery to use a <script> tag (dataType script + crossDomain) so MathJax finds its root/config again.
# Only matches the un-patched loader, so this is safe to run on every start.
find /usr/src/app/public/javascripts/ /usr/src/app/public/dist/ -name "*.js" -type f \
    -exec grep -l 'ajax/libs/mathjax/[0-9.]*/MathJax\.js?config=' {} + 2>/dev/null \
    | xargs -r sed -i -E 's#(/ajax/libs/mathjax/[0-9.]+/MathJax\.js\?config=[^,]*,cache:)(true|!0),success:#\1\2,dataType:"script",crossDomain:true,success:#g'

# Make sure every mathjax version the JS asks for exists locally. If canvas asks for a version we don't
# ship, link it to the newest local version so it doesn't 404.
MJ_DIR=/usr/src/app/public/ajax/libs/mathjax
MJ_NEWEST=$(ls -1 "$MJ_DIR" 2>/dev/null | grep -E '^[0-9]+(\.[0-9]+)*$' | sort -V | tail -1)
if [ -n "$MJ_NEWEST" ]; then
    for v in $(grep -rhoE 'ajax/libs/mathjax/[0-9]+(\.[0-9]+)+/MathJax\.js' /usr/src/app/public/javascripts/ /usr/src/app/public/dist/ 2>/dev/null \
            | sed -E 's#ajax/libs/mathjax/([0-9.]+)/MathJax\.js#\1#' | sort -u); do
        if [ ! -e "$MJ_DIR/$v" ]; then
            echo "MathJax $v requested by canvas but not found locally - linking to $MJ_NEWEST"
            ln -s "$MJ_NEWEST" "$MJ_DIR/$v"
        fi
    done
fi

# Copy over public folder to volume so it can be used for accelerated sendfile
# NOTE - this is destructive to the volume folder sendfile
# NOTE - changed over to sync_static_files.py run by supervisor when changes detected
#rsync -av --delete /usr/src/app/public /usr/src/app/sendfile/


rm -f /usr/src/app/log/app_init
touch /usr/src/app/log/app_starting

# Make sure no old server pid file is present
rm -f /usr/src/app/tmp/pids/server.pid

echo "=== Launching supervisord ==="
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf


# ===== SCRATCH PAD =====
# Adding dev key?
#psql -U canvas -d canvas_development -c "INSERT INTO developer_keys (api_key, email, name, redirect_uri) VALUES ('test_developer_key', 'canvas@example.edu', 'Canvas Docker', 'http://localhost:8000');"

# 'crypted_token' value is hmac sha1 of 'canvas-docker' using default config/security.yml encryption_key value as secret
#psql -U canvas -d canvas_development -c "INSERT INTO access_tokens (created_at, crypted_token, developer_key_id, purpose, token_hint, updated_at, user_id) SELECT now(), '4bb5b288bb301d3d4a691ebff686fc67ad49daa8', dk.id, 'canvas-docker', '', now(), 1 FROM developer_keys dk where dk.email = 'canvas@example.edu';"
