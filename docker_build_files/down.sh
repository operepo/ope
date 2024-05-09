#!/bin/sh

compose=`which docker-compose`

if [ -z "$compose" ]; then
  compose="docker compose"
fi;
echo "Using Compose: $compose"



#docker-compose down --remove-orphans
$compose down --remove-orphans
