#!/bin/bash
set -e

# Make sure the config file has the proper host name in it
sed "s/<VIRTUAL_HOST>/$VIRTUAL_HOST/g" /config/jsbin.json.template > /config/jsbin.json

# Run jsbin
exec jsbin
