#!/usr/bin/python
import os

repo_name = "operepo"
save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes/app_images")

# Ensure the app_images folder exists
try:
	os.makedirs(save_path)
except:
	pass
	# Should have an exception if it already exists


# Find enabled images and export them to the images folder
def processFolder(cwd=""):
	global save_path, repo_name
	ret = ""
	if (os.path.isfile(cwd) != True):
		#print "Not a file, skipping..."
		return ret
	
	
	dname = os.path.basename(cwd)
	if (dname.startswith("ope-")):
		print "\t============================================"
		print "\tProcessing Image " + dname
		print "\t============================================"
		img_path = os.path.join(save_path, dname)
		os.system("docker load -i " + img_path)
	
	

	return ret
	
# Loop through the folders and find containers with .enabled files.
pwd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes/app_images")
for folder in os.listdir(pwd):
	#print folder
	processFolder(os.path.join(pwd, folder))
