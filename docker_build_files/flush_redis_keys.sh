#!/bin/bash

docker-compose exec ope-redis sh -c "redis-cli flushdb"
# flushall clears ALL dbs.


