#!/bin/sh

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")
ROOTDIR=$(dirname "$BASEDIR")

cd "$BASEDIR"

systemctl disable rpcbind
systemctl stop rpcbind

# change to force update/checkout after adjusting gitattribute linefeeds

# Need these loaded for tftp server to work
echo "Ensuring kernel modules are loaded..."
modprobe nf_conntrack_tftp
echo "nf_conntrack_tftp" > /etc/modules-load.d/nf_conntrack_tftp.conf
modprobe nf_nat_tftp
echo "nf_nat_tftp" > /etc/modules-load.d/nf_nat_tftp.conf
modprobe nf_conntrack_ftp
echo "nf_conntrack_ftp" > /etc/modules-load.d/nf_conntrack_ftp.conf
modprobe nf_conntrack_netbios_ns
echo "nf_conntrack_netbios_ns" > /etc/modules-load.d/nf_conntrack_netbios_ns.conf
modprobe nfs
echo "nfs" > /etc/modules-load.d/nfs.conf
modprobe nfsd
echo "nfsd" > /etc/modules-load.d/nfsd.conf
modprobe ipip
echo "ipip" > /etc/modules-load.d/ipip.conf


# Add some rules to track tftp traffic
#WLAN_IF=eth0
#iptables -A INPUT -i $WLAN_IF -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
#iptables -A INPUT -i $WLAN_IF -p udp --dport 69 -m state --state NEW -j ACCEPT


build_flag=""
if [ ! -z "$1" ]; then
  build_flag="$1"
fi

rebuild_param=""
if [ "$build_flag" = "auto" ]; then
  rebuild_param="auto"
fi
echo "Rebuilding docker compose..."
python $ROOTDIR/build_tools/rebuild_compose.py "$rebuild_param"

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
