#!/bin/bash

# https://en.opensuse.org/SDB:System_upgrade
### ONLINE Update for OpenSuse 42.1 to 42.3 ###

# Tell Zypper to keep copies of RPM files after update (so we can send those to offline server)
# This adds keeppackages=1 to all /etc/zypp/repos.d/*
zypper modifyrepo -k --all


# Update OpenSuse from 42.1 to 42.3
# Make sure up to date at 42.1
zypper refresh
zypper update

# Backup repos
cp -Rv /etc/zypp/repos.d /etc/zypp/repos.d.Old
# Change repo file names
sed -i 's/42.1/42.3/g' /etc/zypp/repos.d/*

zypper refresh
zypper dup --download-in-advance


# Copy packages to USB drive
/var/cache/zypp/packages

# Reboot the server so new kernel is active
# reboot