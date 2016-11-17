#!/usr/bin/python
import os



# Find enabled images and export them to the images folder

def processFolder(cwd=""):
	ret = ""
	if (os.path.isdir(cwd) != True):
		#print "Not a folder, skipping..."
		return ret
	
	enabled = os.path.join(cwd, ".enabled")
	if (os.path.isfile(enabled) != True):
		#print "Not enabled, skipping " + cwd
		return ret
	
	dname = os.path.basename(cwd)
    print "\t============================================"
	print "\tProcessing Image " + dname
    print "\t============================================"
	os.system("docker save -o images/" + dname + ".tar " + dname)
	
	

	return ret
	
# Loop through the folders and find containers with .enabled files.
pwd = os.getcwd()
for folder in os.listdir("."):
	processFolder(os.path.join(pwd, folder))
