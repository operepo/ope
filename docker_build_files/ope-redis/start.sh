#!/bin/sh

# Get the current free memory
SET FREE_MEM=`awk '/MemFree/ {printf "%.3f \n", $2/1024/1024 }' /proc/meminfo`

# Get the current total memory
SET TOTAL_MEM=`awk '/MemTotal/ {printf "%.3f \n", $2/1024/1024 }' /proc/meminfo`

# Decide how much memory to allocate to Redis
SET REDIS_MEM=1024

# Copy the redis conf and set the memory value
echo "=== Applying config settings ==="
cp /etc/redis.conf.tmpl /etc/redis.conf
sed -i "s/<REDIS_MEM>/${REDIS_MEM}/" /etc/redis.conf

echo "=== Launching redis ==="
exec redis-server /etc/redis.conf
