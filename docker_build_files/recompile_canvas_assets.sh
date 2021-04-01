#!/bin/bash

docker-compose exec ope-canvas bash -c "cd /usr/src/app; bundle exec rake canvas:compile_assets"


