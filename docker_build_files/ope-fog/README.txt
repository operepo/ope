
========= PORT MAPPING FOR TFTP ====================

On the host machine make sure the following modules are loaded

modprobe nf_conntrack_tftp
modprobe nf_nat_tftp


Make sure to forward tftp in from public address


# Inside Host
iptables -t nat -A POSTROUTING -j MASQUERADE



WIN MACHINES - need to have firewall setup to allow tftp or be disabled if 
you are testing/using tftp 
