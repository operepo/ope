#!/usr/bin/python
import os
import subprocess

repo_name = "operepo"
tag = "release"
save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes/app_images")

# Ensure the app_images folder exists
try:
    os.makedirs(save_path)
except:
    pass
    # Should have an exception if it already exists

# Get the digest of the docker image
def get_app_digest(app_name):
    global save_path, repo_name, tag
    
    proc = subprocess.Popen(["/usr/bin/docker", "images", repo_name + "/" + app_name + ":" + tag], stdout=subprocess.PIPE)
    lines = proc.stdout.readlines()
    ret = "..."
    for line in lines:
        # Go through each line and find the digest for the latest tagged item
        parts = line.split()
        if parts[0] == repo_name + "/" + app_name and parts[1] == tag:
            #print("\tFound digest: " + parts[2] + " for: " + repo_name + "/" + app_name + ":" + tag)
            ret = parts[2]
    
    return ret

def save_app_digest(app_name, digest):
    global save_path, repo_name
    
    # Store the digest in the app path
    digest_path = os.path.join(save_path, app_name + ".digest")
    try:
        f = open(digest_path, "w")
        f.write(digest)
        f.close()
    except:
        # Unable to save?
        pass
    

def get_tar_digest(app_name):
    global save_path, repo_name
    
    tar_digest = "."
    digest_path = os.path.join(save_path, app_name + ".digest")
    # Open the file and read the digest of the currently saved tar file
    try:
        f = open(digest_path,  "r")
        tmp = f.read().strip()
        if tmp != "":
            tar_digest = tmp
        f.close()
    except:
        # Unable to load last digest, just leave it empty
        tar_digest = "."
        
    return tar_digest

def load_app(app_name):
    global save_path, repo_name, tag
    
    img_path = os.path.join(save_path, app_name + ".tar.gz")
    
    
    # Load the last saved tar digest
    tar_digest = get_tar_digest(app_name)
    # Load the current docker digest
    app_digest = get_app_digest(app_name)
    print("Digests (tar/app): " + tar_digest + "/" + app_digest)
    if app_digest != tar_digest or app_digest == "..." or tar_digest == "..":
        # Save the binary
        print("\tApp modified, importing with docker load from: " + img_path)
        os.system("docker load -i " + img_path)
        
        # Update the digest
        app_digest = get_app_digest(app_name)
        save_app_digest(app_name, app_digest)
    else:
        # App hasn't changed
        print("\tApp hasn't changed, skipping.")
    
  
def processFolder(cwd=""):
    global save_path, repo_name
    ret = ""
    if (os.path.isdir(cwd) != True):
        #print("Not a folder, skipping...")
        return ret
    
    enabled = os.path.join(cwd, ".enabled")
    if (os.path.isfile(enabled) != True):
        #print("Not enabled, skipping " + cwd)
        return ret
    
    dname = os.path.basename(cwd)
    print("============================================")
    print(" Processing Image " + dname)
    print("============================================")
    load_app(dname)
    
    return ret

    # Find enabled images and export them to the images folder
# def processFolder(cwd=""):
    # global save_path, repo_name
    # ret = ""
    # if (os.path.isfile(cwd) != True):
        #print("Not a file, skipping...")
        # return ret
    
    
    # dname = os.path.basename(cwd)
    # if (dname.startswith("ope-")):
        # print("\t============================================")
        # print("\tProcessing Image " + dname)
        # print("\t============================================")
        # img_path = os.path.join(save_path, dname)
        # os.system("docker load -i " + img_path)

    # return ret


if __name__ == "__main__":
    # Loop through the folders and find containers with .enabled files.
    pwd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker_build_files")
    for folder in os.listdir(pwd):
        processFolder(os.path.join(pwd, folder))
