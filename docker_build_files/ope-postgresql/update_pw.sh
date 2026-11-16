#!/bin/bash

# Set the postgres password to IT_PW (run inside the container, e.g. docker exec -e IT_PW=... ope-postgresql /update_pw.sh)
echo "Updating pw..."
psql -v ON_ERROR_STOP=1 -U postgres --no-psqlrc --set pw="$IT_PW" <<-'EOSQL'
	ALTER USER postgres WITH PASSWORD :'pw' ;
EOSQL
