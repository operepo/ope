#!/bin/bash


compose=`which docker-compose`

if [ -z "$compose" ]; then
  compose="docker compose"
fi;
echo "Using Compose: $compose"


$compose exec ope-canvas bash -c "cd /usr/src/app; bundle exec rake canvas:compile_assets"


