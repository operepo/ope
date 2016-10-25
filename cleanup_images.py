#!/usr/bin/python

import os

# Remove old images and volumes

# Cleanup old volumes
# docker volume rm $(docker volume ls -qf dangling=true)
os.system("docker volume rm $(docker volume ls -qf dangling=true)")

# Cleanup old images
# docker rmi $(docker images -f "dangling=true" -q)
os.system("docker rmi $(docker images -f \"dangling=true\" -q)")

# Cleanup old containers
# docker rm -v $(docker ps -a -q -f status=exited)
os.system("docker rm -v $(docker ps -a -q -f status=exited)")
