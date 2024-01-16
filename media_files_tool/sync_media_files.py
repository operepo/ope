from __future__ import print_function
from __future__ import unicode_literals


import sys
import os
#import getpass
from prompt_toolkit import prompt, ANSI
import logging
import paramiko
import requests
import requests
import json
from requests import ConnectionError, Session
import color
from color import p, tr

# Disable test ssl warnings.
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


APP_FOLDER = None

def get_app_folder():
    global Logger, APP_FOLDER
    ret = ""
    # Adjusted to save APP_FOLDER - issue #6 - app_folder not returning the same folder later in the app?
    if APP_FOLDER is None:
        # return the folder this app is running in.
        # Logger.info("Application: get_app_folder called...")
        if getattr(sys, 'frozen', False):
            # Running in pyinstaller bundle
            ret = sys._MEIPASS
            # Logger.info("Application: sys._MEIPASS " + sys._MEIPASS)
            # Adjust to use sys.executable to deal with issue #6 - path different if cwd done
            # ret = os.path.dirname(sys.executable)
            # Logger.info("AppPath: sys.executable " + ret)

        else:
            ret = os.path.dirname(os.path.abspath(__file__))
            # Logger.info("AppPath: __file__ " + ret)
        APP_FOLDER = ret
        # Add this folder to the os path so that resources can be found more reliably
        text_dir = os.path.join(APP_FOLDER, "kivy\\core\\text")
        os.environ["PATH"] = os.environ["PATH"] + ";" + ret + ";" + text_dir
        print("-- ADJUSTING SYS PATH -- " + os.environ["PATH"])

    else:
        ret = APP_FOLDER
    return ret


# Run as app starts to make sure we save the current app folder
# in response to issue #6
get_app_folder()
print("APP FOLDER " + APP_FOLDER)

# Deal with issue #12 - No handlers could be found for logger "paramiko.transport"
paramiko.util.log_to_file("ssh.log")
logging.raiseExceptions = False

# Use transfer friendly cipher
paramiko.Transport._preferred_ciphers = ('blowfish-cbc', 'aes128-gcm', 'aes128-ctr', 'aes192-ctr', 'aes256-ctr', 'aes128-cbc', 'aes192-cbc', 'aes256-cbc', '3des-cbc')
# 'aes128-ctr', 'aes192-ctr', 'aes256-ctr', 'aes128-cbc', 'aes192-cbc', 'aes256-cbc', 'blowfish-cbc', '3des-cbc'

# paramiko_logger = logging.getLogger('paramiko.transport')
# if not paramiko_logger.handlers:
#    console_handler = logging.StreamHandler()
#    console_handler.setFormatter(
#        logging.Formatter('%(asctime)s | %(levelname)-8s| PARAMIKO: '
#                      '%(lineno)03d@%(module)-10s| %(message)s')
#    )
# paramiko_logger.addHandler(console_handler)


def make_folders():
    global APP_FOLDER

    # Make sure imscc_files is present
    t_path = os.path.join(APP_FOLDER, "imscc_files")
    if not os.path.exists(t_path):
        os.makedirs(t_path, exist_ok=True)
    

    # make sure media_files is present (and create the media.files link)
    t_path = os.path.join(APP_FOLDER, "media_files")
    if not os.path.exists(t_path):
        os.makedirs(t_path, exist_ok=True)

    # Make sure documents is present
    t_path = os.path.join(APP_FOLDER, "media_files/documents")
    if not os.path.exists(t_path):
        os.makedirs(t_path, exist_ok=True)
    
    t_path = os.path.join(APP_FOLDER, "media_files/media.files")
    if not os.path.exists(t_path):
        f = open(t_path, "w")
        f.write("Place holder - do not delete!")
        f.close()

    # make sure media is present
    t_path = os.path.join(APP_FOLDER, "media_files/media")
    if not os.path.exists(t_path):
        os.makedirs(t_path, exist_ok=True)


def get_input_value(input_prompt="", default="", min_length=1, is_password=False):
    input_value = ""
    try_again = ""
    while len(input_value) < min_length:
        if try_again != "":
            p(try_again)
        prompt_str = "}}yn" + input_prompt
        if len(default) > 1:
            prompt_str += "[default " + default + "]"
        prompt_str += ": }}xx"
        #p(prompt_str, end='')
        input_value = prompt(ANSI(tr(prompt_str)), is_password=is_password)
        # Strip off extra spaces and line feeds
        input_value = input_value.strip()
        if input_value == "" and len(default) > 1:
            # Use default value
            input_value = default
        
        try_again = "}}rnInvalid input - try again...}}xx"
    return input_value

def find_media_folder():
    # Look for media.files file in the media folder
    found = False
    
    # Get current path
    app_path = get_app_folder()
    
    # See if media_files/media.files exists
    test_path = os.path.join(app_path, "media_files/media.files")
    if os.path.exists(test_path):
        # Found media files path
        found = os.path.dirname(test_path)
    
    if found is False:
        # Try next path - ../media_files/media.files
        test_path = os.path.normpath(os.path.join(app_path, "../media_files/media.files"))
        if os.path.exists(test_path):
            found = os.path.dirname(test_path)
        
    return found

def connect_ssh(server, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server, username=user, password=password, compress=True, look_for_keys=False, timeout=6)
        return ssh
    except paramiko.ssh_exception.BadHostKeyException:
        p("}}rn - SSH - Invalid Host key!}}xx")
        return None
    except paramiko.ssh_exception.BadAuthenticationType as ex:
        p("}}rn - SSH Bad auth - Check your login credentials!}}xx")
        return None
    except Exception as ex:
        p("}}rn - SSH Unknown Error - %s}}xx" % str(ex))
        return None
    
def copy_callback(transferred, total):
        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        #p(".", end=False)
        #return
        if total == 0:
            p("\r\t\t\t [##########]", end=False)
        else:
            val = int(float(transferred) / float(total) * 100)
            if val < 0:
                val = 0
            if val > 100:
                val = 100
        
        progress_str = "#" * int(val / 10)
        progress_str = "{:<10}".format(progress_str)
        p("\r [%s ]" % progress_str, end=False)

def sync_folder(sftp, local_folder, remote_folder):
    # Get the list of local files
    items = os.listdir(local_folder)
    
    for item in items:
        local_path = os.path.join(local_folder, item)
        remote_path = os.path.join(remote_folder, item).replace("\\", "/")
        if os.path.isdir(local_path):
            #p("}}cn Folder: %s -> %s}}xx" % (local_path, remote_path))
            try:
                sftp.chdir(remote_folder)
            except Exception as ex:
                p("\t ERROR - Invalid remote path! " + remote_folder + "\n" + ex)
                return
            try:
                sftp.mkdir(item)
            except:
                # Will fail if directory already exists
                pass
            sync_folder(sftp, local_path, remote_path)
        else:
            p("\n}}cn --> Sending: %s}}xx" % item)
            # Push file
            sftp.put(local_path, remote_path, callback=copy_callback)
        
    
    return
    

def push_main():

    p("}}cs\n\n}}mb=======================================\n| OPE Media File Sync Tool          |\n=======================================\n}}xx")
    p("")
    p("}}wnThis tool will help you copy media files to your SMC server so that they work in an offline environment.}}xx")
    p("")
    p("")
    smc_server = get_input_value("Enter SMC server IP or name", default="smc.ed", min_length=5)
    p("}}gn - Using " + smc_server)
    smc_user = get_input_value("Enter SMC SSH User (ope for ubuntu, root or opensuse)", default="ope", min_length=3)
    p("}}gn - using " + smc_user)
    smc_password = get_input_value("Enter SMC SSH Password }}cn(characters will be masked)}}yn", default="", min_length=5, is_password=True)
    remote_smc_folder = get_input_value("Enter SMC Volumes Folder [/home/ope/ope/volumes/smc (ubuntu - default) or /ope/volumes/smc (old opensuse)]", default="/home/ope/ope/volumes/smc", min_length=9)
    remote_media_folder = os.path.join(remote_smc_folder, "media").replace("\\", "/")
    remote_documents_folder = os.path.join(remote_smc_folder, "documents").replace("\\", "/")
    p("}}gn - using %s}}xx" % remote_smc_folder)
    
    p("}}ynLooking for local media_files folder...}}xx")
    media_folder = find_media_folder()
    if media_folder is False:
        p("}}rbERROR!!! - Unable to locate media_files folder!}}xx")
        sys.exit(-1)
    p("}}gn - using path %s}}xx" % media_folder)
    local_media_folder = os.path.join(media_folder, "media")
    local_documents_folder = os.path.join(media_folder, "documents")
    
    # Try connecting to the SSN server
    p("\n\n}}gnConnecting...}}xx")
    ssh = connect_ssh(smc_server, smc_user, smc_password)
    if ssh is None:
        p("}}rbERROR!!! - Unable to connect to SMC (ssh) server!}}xx")
        sys.exit(-1)
    
    # Connect to sftp server
    sftp = ssh.open_sftp()

    # Make sure the remote paths exist
    try:
        sftp.chdir(remote_media_folder)
    except IOError as ex:
        p("}}rbERROR!!! - Remote folder does not exist " + remote_media_folder + "}}xx")
        sys.exit(-1)
    try:
        sftp.chdir(remote_documents_folder)
    except IOError as ex:
        p("}}rbERROR!!! - Remote folder does not exist " + remote_documents_folder + "}}xx")
        sys.exit(-1)
    
    p("}}gnSyncing Media Files...}}xx")
    if sync_folder(sftp, local_media_folder, remote_media_folder) is False:
        p("}}rbERROR!!! - Unable to sync media files folder to SMC!}}xx")
        sys.exit(-1)
    
    p("}}gnSyncing Document Files...}}xx")
    if sync_folder(sftp, local_documents_folder, remote_documents_folder) is False:
        p("}}rbERROR!!! - Unable to sync document files folder to SMC!}}xx")
        sys.exit(-1)
    
    sftp.close()
    ssh.close()
    p("}}gnMedia Files Synced Succesfully!}}xx")
    
def pull_main():
    p("}}cs\n\n}}mb=======================================\n| OPE Media File Sync Tool          |\n=======================================\n}}xx")
    p("")
    p("}}wnThis tool will help you pull media files from your SMC so that you can take them to an offline environment.}}xx")
    p("")
    p("")
    course_code = get_input_value("Enter the course code for your canvas class: ", default="ACCT101", min_length=3)
    p("}}gn - Using " + course_code)
    smc_server = get_input_value("Enter SMC server IP or name", default="https://smc.ed", min_length=5)
    p("}}gn - Using " + smc_server)
    
    p("}}ynLooking for local media_files folder...}}xx")
    media_folder = find_media_folder()
    if media_folder is False:
        p("}}ybWARNING - Missing media_files folder}}xx")
        create_prompt = get_input_value(" - do you want to create the folders?  (y/n)", default="y", min_length=1)
        create_prompt = create_prompt.lower()
        if create_prompt == "y":
            make_folders()
        
        media_folder = find_media_folder()
        
    if media_folder is False:
        p("}}rbERROR!!! - Unable to locate media_files folder!}}xx")
        sys.exit(-1)

    p("}}gn - using path %s}}xx" % media_folder)
    local_media_folder = os.path.join(media_folder, "media")
    local_documents_folder = os.path.join(media_folder, "documents")
    
    if not smc_server.startswith("https://"):
        smc_server = "https://" + smc_server
    if not smc_server.endswith("/"):
        smc_server = smc_server + "/"

    query_url = smc_server + "media/media_list.json"

    p("}}ynGetting list of media files from SMC:}}xx  " + query_url + "...")

    data = {}
    data["search_term"] = course_code
    try:
        resp = requests.post(query_url, verify=False, data=data)
    except ConnectionError as ex:
        p("}}rbERROR - Unable to communicate with SMC server: }}xx" + str(ex))
        return False
    
    if resp is None:
        p("}}rbERROR - Empty response from the SMC server!}}xx")
        return False
    
    had_errors = False

    try:
        resp.raise_for_status()

        j_data = resp.json()
        # Look in json data for media file list.
        for item in j_data:
            # Get the list of files for this media item (e.g. mp4, json, ccaption)
            file_list = item["files"]
            file_type = item["file_type"]
            if file_type == "media":
                item_guid = item["media_guid"]
                base_path = local_media_folder
            elif file_type == "document":
                item_guid = item["document_guid"]
                base_path = local_documents_folder
            else:
                p("}}rbUnknown File Type!}}xx")
                had_errors = True
                continue
            
            for f in file_list:
                m_url = smc_server + f
                file_name = os.path.basename(f)
                prefix = file_name[:2]
                
                m_path = os.path.join(base_path, prefix + "/" + file_name)

                # Does file exist?
                if os.path.exists(m_path):
                    p("   }}yb - File already downloaded: " + m_path)
                    continue

                # File doesn't exist, download it
                p(" }}yn- Pulling }}xx" + m_url) # + " -> " + m_path)
                # Ensure the folders exist
                os.makedirs(os.path.join(base_path, prefix), exist_ok=True)
                # Download and save the file
                try:
                    with requests.get(m_url, verify=False, stream=True) as r:
                        r.raise_for_status()
                        with open(m_path + ".download", "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        # Move the file to its non DL name
                        os.rename(m_path+".download", m_path)

                except Exception as ex:
                    p("}}rbERROR - Unable to download file: " + m_url + "}}xx\n" + str(ex))
                    had_errors = True
                    continue
              
    except Exception as ex:
        p("}}rbERROR - Invalid response from SMC server. This requires SMC v1.9.56+ to work.\n" + str(ex))
        had_errors = True
        return False

    p("}}gbDone.}}xx")

    if had_errors:
        p("}}rbWARNING - One or more files failed to download!}}xx")
    return True

if __name__ == "__main__":
    cmd = "push"
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    if cmd == "pull":
        pull_main()
    else:
        push_main()
    