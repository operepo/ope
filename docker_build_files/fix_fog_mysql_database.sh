#!/bin/bash

# If fog (mysql) is working really hard and slowing down the server - run this to stop/repair/start the mysql service.


compose=`which docker-compose`

if [ -z "$compose" ]; then
  compose="docker compose"
fi;
echo "Using Compose: $compose"

# Stop the mysql service
# Run the repair tool
# Start the mysql service

$compose exec ope-fog bash -c ""
#$compose exec ope-postgresql bash -c "psql -U postgres -d canvas_production -c 'drop index index_role_overrides_on_context_role_permission;'"


