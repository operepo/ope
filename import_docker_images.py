#!/usr/bin/python
import os



# Find enabled images and export them to the images folder

def processFolder(cwd=""):
	ret = ""
	if (os.path.isfile(cwd) != True):
		#print "Not a file, skipping..."
		return ret
	
	
	dname = os.path.basename(cwd)
	if (dname.startswith("ope-")):
		print "Processing Image " + dname
		os.system("docker load -i " + cwd)
	
	

	return ret
	
# Loop through the folders and find containers with .enabled files.
pwd = os.getcwd()
pwd = os.path.join(pwd, "images")
for folder in os.listdir("./images/"):
	#print folder
	processFolder(os.path.join(pwd, folder))
