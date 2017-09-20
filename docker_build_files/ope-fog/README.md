
# Fog imaging server - running in docker container

## Description
A conversion of the fogproject imaging server running in a docker container

The container is designed to run from docker-compose in the OPE project. The compose
configuration properly exposes ports. The up.sh script in the compose folder makes sure
that the host loads the needed modules and rebuilds the compose file based on the
current IP, domain, and password.

## Implementation details

Special settings are in place to deal with FTP, TFTP, and NFS protocols.

The container is launched with the following privileges:
privileged: true
cap_add:
    - NET_ADMIN
    - SYS_ADMIN

This runs as a BRIDGED network, NOT a HOST network. Services are set to use static ports
to allow nat port forwarding to work properly.

# Host changes
These settings should be taken care of if lauched via the up.sh script.

This is setup to run on a linux host (openSuse 42.1). It hasn't run properly in
docker for windows, though it should be possible.

## TFTP
The docker host needs to have the following changes in place to support TFTP and allow
for traffic to flow through the NAT adaptor properly

modprobe nf_conntrack_tftp
modprobe nf_nat_tftp

# Add some rules to track tftp traffic
WLAN_IF=eth0
iptables -A INPUT -i $WLAN_IF -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i $WLAN_IF -p udp --dport 69 -m state --state NEW -j ACCEPT

## NFS/FTP
The following modules need to be loaded on the host for FTP and NFS to work
modprobe nf_conntrack_ftp
modprobe nf_conntrack_netbios_ns
modprobe nfs
modprobe nfsd


# Container Changes
Inside the container, adjustments were made to FTP, NFS, TFTP to specify static ports
so that they can be exposed form docker properly.

The container needs this on to allow proper tracking/routing of UDP packets for TFTP/NFS
iptables -t nat -A POSTROUTING -j MASQUERADE

On startup, the container should adjust itself and set the passwords based on the compose 
environment variables.

update_fog_ip.py runs on startup and should adjust the IP settings in fog automatically.

Services are modified to use static ports or specific ranges (e.g. ftp in passive mode, etc...)


# TODO
- Need to set root password on startup
