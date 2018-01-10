#!/bin/bash


# Rules to forward multicast packets modprobe 
iptables -I INPUT -m pkttype --pkt-type multicast -j ACCEPT
iptables -I FORWARD -m pkttype --pkt-type multicast -j ACCEPT
iptables -I OUTPUT -m pkttype --pkt-type multicast -j ACCEPT
iptables -I FORWARD -p igmp -j ACCEPT
iptables -I FORWARD -p icmp -j ACCEPT
iptables -I INPUT -i lo -j ACCEPT
iptables -I FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -I FORWARD -p udp --dport 9000-9010 -m conntrack --cstate NEW -j ACCEPT


iptables -t mangle -I PREROUTING -d 224.0.0.0/4 -j TTL --ttl-set 64
#iptables -A -d 224.0.0.0/4 -j MULTICAST
#iptables -A INPUT   -s 224.0.0.0/4 -j ACCEPT
#iptables -A FORWARD -s 224.0.0.0/4 -d 224.0.0.0/4 -j ACCEPT
#iptables -A OUTPUT  -d 224.0.0.0/4 -j ACCEPT


# Rules to forward TFTP packets
#WLAN_IF=eth0
#iptables -A INPUT -i $WLAN_IF -p udp -m state --state ESTABLISHED,RELATED -j ACCEPT
#iptables -A INPUT -i $WLAN_IF -p udp --dport 69 -m state --state NEW -j ACCEPT


#igmpproxy -vv -d /etc/igmpproxy.conf
pimd -f -d

