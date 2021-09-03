#!/usr/bin/python

import os
import paramiko
from getpass import getpass

# Intiailize git repos on the docker server

# TODO - pull from env file?
docker_host = "docker.pencollege.net"
docker_user = "root"
docker_password = ""
ope_path = "/ope"

if (docker_password == ""):
    docker_password = getpass("Please enter Password for the docker server: ")
docker_password = docker_password.strip()
ope_path = ope_path.strip()

# Setup inital ssh connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(docker_host, username=docker_user, password=docker_password)
except Exception as e:
    print("Error logging into " + docker_user + "@" + docker_host + "  --> " + str(e))
    exit()
# Open SFTP
sftp = ssh.open_sftp()

# Copy images
choice = raw_input("Copy Images? Y or N [enter for Y]: ")
choice = choice.tolower().strip()
if (choice == "y"):
    pwd = os.getcwd()
    pwd = os.path.join(pwd, "images")
    for folder in os.listdir("./images/"):
        #print(folder)
        fname = os.path.basename(folder)
        dpath = os.path.join(os.path.join(ope_path, "images"), fname).replace("\\", "/")
        spath = os.path.join(pwd, fname).replace("/", "\\")
        print("From: " + spath + " --> " + dpath)
        # Send the image
        sftp.put(spath, dpath)
        # Import it into the docker machines
        stdin, stdout, stderr = ssh.exec_command("cd " + ope_path + "; docker load -i images/" fname)
        print(stdout)

# Ensure bare git repos
stdin, stdout, stderr = ssh.exec_command("cd " + ope_path + "; if [-d repos/ope.git] ")

    
sftp.close()
ssh.close()