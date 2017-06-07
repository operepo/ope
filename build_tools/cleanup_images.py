#!/usr/bin/python

import os

# Remove old images and volumes

# Cleanup old volumes
# docker volume rm $(docker volume ls -qf dangling=true)
# TODO prevent removing ope_ named volumes so we don't loose data
#os.system("docker volume rm $(docker volume ls -qf dangling=true)")

# Cleanup old containers
# docker rm -v $(docker ps -a -q -f status=exited)
os.system("powershell \"docker rm -v $(docker ps -a -q -f status=exited)\"")

# Cleanup old images
# docker rmi $(docker images -f "dangling=true" -q)
os.system("powershell \"docker rmi $(docker images -f dangling=true -q)\"")


