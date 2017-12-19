#!/bin/sh

# change to force update/checkout after adjusting gitattribute linefeeds

# Need these loaded for tftp server to work
#### Moved to ope-router so it runs on auto startup after a reboot
#echo "Ensuring tftp kernel modules are loaded..."
#modprobe nf_conntrack_tftp
#modprobe nf_nat_tftp
#modprobe nf_conntrack_ftp
#modprobe nf_conntrack_netbios_ns
#modprobe nfs
#modprobe nfsd


# Add some rules to track tftp traffic
#### Moved to ope-router
#WLAN_IF=eth0
#iptables -A INPUT -i $WLAN_IF -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
#iptables -A INPUT -i $WLAN_IF -p udp --dport 69 -m state --state NEW -j ACCEPT


echo "Rebuilding docker compose..."
python ../build_tools/rebuild_compose.py

build_flag=""
if [ ! -z "$1" ]; then
  build_flag="$1"
fi

if [ "$build_flag" = "b" ]; then
  echo "Building docker containers..."
  docker-compose build
fi

echo "Bringing up containers..."
# Bring up without rebuilding (in case container is out of date it will still start)
docker-compose up -d --no-build --remove-orphans


#echo "Bringing up bridge for fog..."
#ope-fog/pipework br-ope ope-fog 192.168.10.27/24
#brctl addif br10 eth0
#ip addr add 192.168.10.27/24 dev br10

echo "Done!"
