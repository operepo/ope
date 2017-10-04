#!/bin/bash

git daemon --reuseaddr --user=git --export-all --verbose --base-path=/home/www-data/git/ /home/www-data/git/

