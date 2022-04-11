#!/bin/sh

# Get the current free memory
FREE_MEM=`awk '/MemFree/ {printf "%.0f \n", $2/1024/1024 }' /proc/meminfo`

# Get the current total memory
TOTAL_MEM=`awk '/MemTotal/ {printf "%.0f \n", $2/1024/1024 }' /proc/meminfo`

# Decide how much memory to allocate to Redis
# TOTAL_MEM should be in gigs
REDIS_MEM="128m"
if [ $TOTAL_MEM -gt 1 ]; then REDIS_MEM="256m"; fi
if [ $TOTAL_MEM -gt 3 ]; then REDIS_MEM="512g"; fi
if [ $TOTAL_MEM -gt 5 ]; then REDIS_MEM="768g"; fi
if [ $TOTAL_MEM -gt 7 ]; then REDIS_MEM="1g"; fi
if [ $TOTAL_MEM -gt 8 ]; then REDIS_MEM="2g"; fi
if [ $TOTAL_MEM -gt 10 ]; then REDIS_MEM="3g"; fi
if [ $TOTAL_MEM -gt 14 ]; then REDIS_MEM="4g"; fi
if [ $TOTAL_MEM -gt 18 ]; then REDIS_MEM="5g"; fi
if [ $TOTAL_MEM -gt 22 ]; then REDIS_MEM="6g"; fi
if [ $TOTAL_MEM -gt 30 ]; then REDIS_MEM="8g"; fi

# Copy the redis conf and set the memory value
echo "=== Applying config settings ==="
cp /etc/redis.conf.tmpl /etc/redis.conf
sed -i "s/<REDIS_MEM>/${REDIS_MEM}/" /etc/redis.conf

echo "=== Launching redis ==="
exec redis-server /etc/redis.conf
