#!/bin/bash

compose=`which docker-compose`

if [ -z "$compose" ]; then
  compose="docker compose"
fi;
echo "Using Compose: $compose"


$compose exec ope-redis sh -c "redis-cli flushdb"
# flushall clears ALL dbs.


