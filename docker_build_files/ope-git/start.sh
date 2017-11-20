#!/bin/bash
#set -e

# TODO  - convert this to https://docs.gitlab.com/omnibus/docker/  gitlab config 



# Make sure the config file has the proper host name in it
#sed "s/<VIRTUAL_HOST>/$VIRTUAL_HOST/g" /config/jsbin.json.template > /config/jsbin.json

# Run jsbin
#exec jsbin

# Cause gitlab to pickup new config settings
gitlab-ctl reconfigure
gitlab-ctl restart

