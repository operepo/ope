#!/usr/bin/python
import os, sys
import socket
import shutil

# USE docker-compose push from the docker_build_files folder
print("Pushing images using docker-compose push...")
cmd = "docker-compose push"
os.system(cmd)
a=raw_input("Press ENTER to quit...")
sys.exit()

# Push images up to dockerhub so they can be pulled later

# Images to push - will fill in with folders that have .enabled files
images = [] #[ "ope-gateway", "ope-dns" ]


# Grab current folder, then move back one, then into the docker_build_files folder
pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pwd = os.path.join(pwd, "docker_build_files")
if not os.path.isdir(pwd):
    print("Unable to find docker build files at: " + pwd)
    sys.exit()
else:
    print("Searching for images to push...")
#print(" " + pwd)
#sys.exit()


# Loop through the folders and find containers with .enabled files.
for folder in os.listdir(pwd):
	if (os.path.isdir(os.path.join(pwd, folder))):
		# See if this has an enabled file in it
		ef = os.path.join(pwd, folder)
		ef = os.path.join(ef, ".enabled")
		if (os.path.isfile(ef)):
			print("Found " + folder + "... adding to push list")
			images.append(folder)


# Push images
for image in images:
	print("Trying to push: " + image)
	cmd = "docker push operepo/operelease:" + image
	print("\t" + cmd)
	os.system(cmddock)
	print "Done."

print("\n\nFinished!")
a = raw_input("Press ENTER key to continue")
