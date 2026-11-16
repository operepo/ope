#!/bin/sh

# Get the current free memory
FREE_MEM=`awk '/MemFree/ {printf "%.0f \n", $2/1024/1024 }' /proc/meminfo`

# Get the current total memory
TOTAL_MEM=`awk '/MemTotal/ {printf "%.0f \n", $2/1024/1024 }' /proc/meminfo`

# Decide how much memory to allocate to Redis
# TOTAL_MEM should be in gigs
REDIS_MEM="128m"
if [ $TOTAL_MEM -gt 1 ]; then REDIS_MEM="256m"; fi
if [ $TOTAL_MEM -gt 3 ]; then REDIS_MEM="512m"; fi
if [ $TOTAL_MEM -gt 5 ]; then REDIS_MEM="768m"; fi
if [ $TOTAL_MEM -gt 7 ]; then REDIS_MEM="1g"; fi
if [ $TOTAL_MEM -gt 8 ]; then REDIS_MEM="2g"; fi
if [ $TOTAL_MEM -gt 10 ]; then REDIS_MEM="3g"; fi
if [ $TOTAL_MEM -gt 14 ]; then REDIS_MEM="4g"; fi
if [ $TOTAL_MEM -gt 18 ]; then REDIS_MEM="5g"; fi
if [ $TOTAL_MEM -gt 22 ]; then REDIS_MEM="6g"; fi
if [ $TOTAL_MEM -gt 30 ]; then REDIS_MEM="8g"; fi

# Copy the redis conf and set the memory value
# Config lives in its own folder so the official entrypoint can make it readable by the redis user
REDIS_CONF=/usr/local/etc/redis/redis.conf
echo "=== Applying config settings (total mem ${TOTAL_MEM}G -> maxmemory ${REDIS_MEM}) ==="
mkdir -p "$(dirname "$REDIS_CONF")"
cp /etc/redis.conf.tmpl "$REDIS_CONF"
sed -i "s/<REDIS_MEM>/${REDIS_MEM}/" "$REDIS_CONF"

echo "=== Launching redis ==="
# Hand off to the official entrypoint - it fixes /data permissions and drops root to the redis user
exec docker-entrypoint.sh redis-server "$REDIS_CONF"
