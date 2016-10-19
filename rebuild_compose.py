#!/usr/bin/python
import os
import socket
import shutil

# Rebuild the docker-compose file

## Write this to the docker-compose.yml file
dc_out = """##### Open Prison Education - Docker Environment #####
# NOTE - This file gets rebuilt, make changes to docker-compose-include.yml file
# 		  in individual container directories and run rebuild_compose.py 
#
# Start docker containers by running this command from the main folder:
#		docker-compose up -d
#
# Stop containers by running this command from the main folder:
#		docker-compose down
#
# START OF docker-compose.yml
version: '2'

services:

"""

# A list of values to substitute in the docker-compose.yml file
replacement_values = { '<DOMAIN>': '', '<IP>': ''}


# Find the local/public ip of the machine
def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	IP = '127.0.0.1'
	try:
		s.connect(('10.255.255.255', 0))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	finally:
		s.close()
	return IP

def processFolder(cwd=""):
	ret = ""
	if (os.path.isdir(cwd) != True):
		#print "Not a folder, skipping..."
		return ret
	
	enabled = os.path.join(cwd, ".enabled")
	if (os.path.isfile(enabled) != True):
		#print "Not enabled, skipping " + cwd
		return ret
	
	print "Processing Folder " + cwd
	
	dc_import = os.path.join(cwd, "docker-compose-include.yml")
	if (os.path.isfile(dc_import) != True):
		print "\t\tSkipping - No docker-compose-include.yml file found"
	
	try:
		f = open(dc_import, "r")
		ret = f.read()
		f.close()
	except:
		print "\t\t Error reading " + dc_import
		ret = ""
	

	return ret


	
#print "Current IP: " + getIP()

# Get current IP address
ip = getIP()
choice = raw_input("Enter public IP [enter to use " + ip + "]: ")
choice = choice.strip()
if (choice != ""):
	ip = choice
replacement_values["<IP>"] = ip
print "Using " + ip + "..."

domain = "ed"
choice = raw_input("Enter domain to use [enter to use " + domain + "]: ")
choice = choice.strip()
if (choice != ""):
	domain = choice
replacement_values["<DOMAIN>"] = domain
print "Using " + domain + "..."


pwd = os.getcwd()

# Make sure the .env file exists
env_file = os.path.join(pwd, ".env")
if (os.path.isfile(env_file) != True):
	# Try to copy the .env.template file
	if (os.path.isfile(os.path.join(pwd, ".env.template")) == True):
		print "\n\t\t\tNew environment file - change values in .env file\n"
		shutil.copy(".env.template", ".env")
	else:
		print "No env file found! Create a .env file to store your settings"

if (os.path.isfile(env_file) == True):
	# Replace template tags with values from the replacement_values array
	
	# Read the current file in
	env_f = open(env_file, "r")
	lines = env_f.read()
	env_f.close()

	# Replace the values
	for key in replacement_values:
		lines = lines.replace(key, replacement_values[key])
	
	# Save the finished env file
	env_f = open(env_file, "w")
	env_f.write(lines)
	env_f.close()
		
# Loop through the folders and find containers with .enabled files.
for folder in os.listdir("."):
	dc_out += processFolder(os.path.join(pwd, folder))

# Replace instances of template tags with values from the replacement_values array
for key in replacement_values:
	dc_out = dc_out.replace(key, replacement_values[key])

# Clear the current docker-compose.yml file and write the new file
docker_compose = open("docker-compose.yml", "w")
docker_compose.write(dc_out)
docker_compose.close()	

print "\n\nFinished!\n\n\tRun commands from main folder\n\t\tTo Build (Online Only): \tdocker-compose build\n\t\tTo start: \t\t\tdocker-compose up -d\n\t\tTo Stop: \t\t\tdocker-compose down"
# Grab all ope- folders and start each one

#pwd = os.getcwd()

#for folder in os.listdir("."):
#  if (folder[:4] == "ope-"):
#    st = "python " + folder + "/start.py"
#    print "Starting " + st
#    os.system(st)