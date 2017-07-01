#!/usr/bin/python
import os, sys
import socket
import shutil

# Rebuild the docker-compose file

## Write this to the docker-compose.yml file
dc_out = """##### Open Prison Education - Docker Environment #####
# NOTE - This file gets rebuilt, make changes to docker-compose-include.yml file
#           in individual container directories and run rebuild_compose.py 
#
# Start docker containers by running this command from the main folder:
#        docker-compose up -d
#
# Stop containers by running this command from the main folder:
#        docker-compose down
#
# START OF docker-compose.yml
version: '2'

<VOLUMES>

services:

"""

# A list of values to substitute in the docker-compose.yml file
replacement_values = { '<DOMAIN>': '', '<IP>': '', "<VOLUMES>": '',
    "<CANVAS_SECRET>": 'sdlkj4342ousoijalke3uosuufodsjvlckxotes'}

# A list of volumes that need to be specified in the volumes section
volume_list = []


def getComposeFolder():
    pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pwd = os.path.join(pwd, "docker_build_files")
    return pwd


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

def getSavedIP():
    # Load the saved IP
    ip = ""
    pwd = getComposeFolder()
    ip_file = os.path.join(pwd, ".ip")
    try:
    	f = open(ip_file, "r")
    	ip = f.read()
    	f.close()
    except:
        print("No saved IP")
    return ip.strip()

def saveIP(ip):
    # Save the ip for later
    # Locate the base folder
    pwd = getComposeFolder()
    ip_file = os.path.join(pwd, ".ip")
    f = open(ip_file, "w")
    f.write(ip)
    f.close()

def saveDomain(domain):
    # Save the domain for later
    pwd = getComposeFolder()
    domain_file = os.path.join(pwd, ".domain")
    f = open(domain_file, "w")
    f.write(domain)
    f.close()

def getDomain():
    # Load saved domain name
    domain = ""
    pwd = getComposeFolder()
    domain_file = os.path.join(pwd, ".domain")
    try:
        f = open(domain_file, "r")
        domain = f.read()
        f.close()
    except:
        print("No saved domain")
    return domain.strip()

def processFolder(cwd=""):
    global volume_list
    
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
        print "        Skipping - No docker-compose-include.yml file found"
    
    try:
        f = open(dc_import, "r")
        ret = f.read()
        f.close()
    except:
        print "         Error reading " + dc_import
        ret = ""
    
    # Make sure to add some line feeds to the end in case the this has tabs on
    # the current line which messes up the yml format
    ret += "\n\n"
    
    # See if we need to import volumes
    vol_import = os.path.join(cwd, "volumes-include.yml")
    if (os.path.isfile(vol_import) != True):
        #print "\t\tNo volumes file."
        return ret
    
    print "\tProcessing volume file: " + vol_import
    
    try:
        f = open(vol_import, "r")
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            # Strip off comments
            i = line.find("#")
            if (i > -1):
                line = line[0:i]
            line = line.strip()
            if (line != ""):
                print "\t===> Volume Found: " + line
                volume_list.append(line)
        f.close()
    except:
        print "\t\tError reading " + vol_import
    
    return ret


    
#print "Current IP: " + getIP()

# Get current IP address
ip = getIP()
saved_ip = getSavedIP()
get_new_ip = False
if ip != saved_ip and saved_ip != "":
    # Looks like your ip has changed?
    print("Possible IP change!!!")
    print("Saved IP: " + saved_ip + " - Machine IP: " + ip)
    choice = raw_input("Do you want to continue to use the saved IP? [Enter for Y, N to enter a new IP]: ")
    if choice.lower() == "n":
        get_new_ip = True
    else:
        # continue with saved ip
        ip = saved_ip

if saved_ip == "" or get_new_ip == True:
    choice = raw_input("Enter public IP [enter to use " + ip + "]: ")
    choice = choice.strip()
    if (choice != ""):
        ip = choice

replacement_values["<IP>"] = ip
print "Using IP: " + ip + "..."
saveIP(ip)

domain = "ed"
saved_domain = getDomain()
if saved_domain == "":
    choice = raw_input("Enter domain to use [enter to use " + domain + "]: ")
    choice = choice.strip()
    if (choice != ""):
        domain = choice
else:
    domain = saved_domain
replacement_values["<DOMAIN>"] = domain
print "Using domain: " + domain + "..."
saveDomain(domain)

# Grab current folder, then move back one, then into the docker_build_files folder
pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pwd = os.path.join(pwd, "docker_build_files")
if not os.path.isdir(pwd):
    print("Unable to find docker build files at: " + pwd)
    sys.exit()
else:
    print("Rebuilding docker compose...")
#print(" " + pwd)
#sys.exit()

# Make sure the .env file exists
env_file = os.path.join(pwd, ".env")
if (os.path.isfile(env_file) != True):
    # Try to copy the .env.template file
    if (os.path.isfile(os.path.join(pwd, ".env.template")) == True):
        print "\n            New environment file - change values in .env file\n"
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

# Make sure the PUBLIC_IP field is updated in the .env file
public_ip_found = False
if os.path.isfile(env_file) == True:
    # Check each line in the file
    ef = open(env_file, "r")
    lines = ef.readlines()
    ef.close()
    
    ef = open(env_file, "w")
    for line in lines:
        if line.startswith("PUBLIC_IP"):
            ef.write("PUBLIC_IP=" + ip + "\n")
            public_ip_found = True
        else:
            ef.write(line)
    if public_ip_found is not True:
        # Didn't find it, add it
        ef.write("\nPUBLIC_IP=" + ip)
    
    ef.close()
# Loop through the folders and find containers with .enabled files.
for folder in os.listdir(pwd):
    dc_out += processFolder(os.path.join(pwd, folder))

# Use the volume_list to create a value for replacement
if (len(volume_list) > 0):
    v = "volumes:\n"
    for vol in volume_list:
        v += "    " + vol + "\n"
    replacement_values["<VOLUMES>"] = v

# Replace instances of template tags with values from the replacement_values array
for key in replacement_values:
    dc_out = dc_out.replace(key, replacement_values[key])

# Clear the current docker-compose.yml file and write the new file
docker_compose = open(os.path.join(pwd,"docker-compose.yml"), "w")
docker_compose.write(dc_out)
docker_compose.close()    

print("\n\nFinished!\n\n    Run commands from docker_build_files folder: {0}\n        To Build (Online Only):     docker-compose build\n        To start:             docker-compose up -d\n        To Stop:             docker-compose down".format(pwd))
# Grab all ope- folders and start each one

#pwd = os.getcwd()

#for folder in os.listdir("."):
#  if (folder[:4] == "ope-"):
#    st = "python " + folder + "/start.py"
#    print "Starting " + st
#    os.system(st)
