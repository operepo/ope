#!/usr/bin/python

#FOG - update IP

# Adjust /opt/fog/.fogsettings
# Change Mysql values
# - DB - fog
#    - globalSettings
#        - update globalSettings set settingValue='??' where settingKey='FOG_TFTP_HOST';
#        - update globalSettings set settingValue='??' where settingKey='FOG_WEB_HOST';
#    - nfsGroupMembers
#        - update nfsGroupMembers set ngmHostename='??' where ngmMemberName='DefaultMember';
# requires these packages and the initial fog setup to be done
# Run this on startup in a docker machine
# apt-get install python-pip python-dev libmysqlclient-dev
# pip install MySQL-python




# Use python3 style print
from __future__ import print_function

import os
import socket
import MySQLdb 
import pdb

if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
            ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0",
            "eth1",
            "eth2",
            "wlan0",
            "wlan1",
            "wifi0",
            "ath0",
            "ath1",
            "ppp0",
        ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


print("Detecting ip...")

# Check environment variable if it exists
ip = os.getenv("PUBLIC_IP")

if ip is None:
    # No environment variable set, try and figure out the current IP
    ip = get_lan_ip()
print("Found IP: {0}".format(ip))


print("Updating fog settings...")

fog_settings_path = "/opt/fog/.fogsettings"

# Read in the old file
filedata = ""
with open(fog_settings_path, 'r') as file:
    filedata = file.readlines()

# While we write it back out, we will grab mysql values for later
# Set them to defaults
mysql_host="localhost"
mysql_user="root"
mysql_pass=""
mysql_db="fog"

# Now write data back out
f = open(fog_settings_path, "w")
for line in filedata:
    if line.startswith("ipaddress="):
        f.write("ipaddress='" + ip + "'\n")
    else:
        f.write(line)
    # Check for mysql values
    if line.startswith("snmysqluser="):
        mysql_user = line.split('=')[-1].strip().strip("'")
    if line.startswith("snmysqlpass="):
        mysql_pass = line.split('=')[-1].strip().strip("'")
    if line.startswith("snmysqlhost="):
        mysql_host = line.split('=')[-1].strip().strip("'")
    if line.startswith("snmysqldb="):
        # NOTE - db is fog, cant set it in .fogsettings?
        mysql_db = line.split('=')[-1].strip().strip("'")

f.close()

#pdb.set_trace()

# Update the mysql server - put new IP in place
db = MySQLdb.connect(host=mysql_host, user=mysql_user,
        passwd=mysql_pass, db=mysql_db, port=3306)
# update TFTP host
cur = db.cursor()
cur.execute("update globalSettings set settingValue='" + ip + "' where settingKey='FOG_TFTP_HOST'")
# Update Web Host
cur = db.cursor()
cur.execute("update globalSettings set settingValue='" + ip + "' where settingKey='FOG_WEB_HOST'")
# Update WOL Host
cur = db.cursor()
cur.execute("update globalSettings set settingValue='" + ip + "' where settingKey='FOG_WOL_HOST'")
# Update storage IP
cur = db.cursor()
cur.execute("update nfsGroupMembers set ngmHostname='" + ip + "' where ngmMemberName='DefaultMember'")

db.close()

# Fix the ip in default.ipxe file
os.system("/bin/sed -i \"s|http://\([^/]\+\)/|http://" + ip + "/|\" /tftpboot/default.ipxe")
os.system("/bin/sed -i \"s|http:///|http://" + ip + "/|\" /tftpboot/default.ipxe")

# Fix the ip in the config.class.php file
os.system("/bin/sed -i \"s|\\\".*\\..*\\..*\\..*\\\"|\\\"" + ip + "\\\"|\" /var/www/fog/lib/fog/config.class.php")

# Run fog installer
#installer_path = "~/trunk/bin"
#installer_file = "installfog.sh"

print("Running fog installer...")
#cmd = "cd " + installer_path + "; ./" + installer_file + " -y"
#print("CMD: " + cmd)
#os.system(cmd)


# Finished
print("Finished updating fog server ip.")

