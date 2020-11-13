import os
import sys
import re
import requests
import logging
import socket
import subprocess

from util import get_human_file_size, get_app_folder

from kivy.uix.filechooser import FileChooser, FileChooserListView, FileChooserIconView, FileSystemAbstract

import paramiko


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

# NOTE - To deal with different profile/home drive paths, we need to set
# the HOME env variable so all instances (git, putty, python) get the same path.
os.environ['HOME'] = os.path.expanduser("~")
print("Using " + os.environ['HOME'] + " as user home folder.")

def get_ssh_connection(ssh_server, ssh_user, ssh_pass):
    # Make sure the id_rsa and id_rsa.pub files exist
    generate_local_ssh_key()

    remove_server_from_known_hosts(ssh_server)

    ssh = None
    err_str = ""
    
    if ssh_server != "" and ssh_user != "" and ssh_pass != "":
        # Connect to server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Load the known_hosts - will save back too
        
        known_hosts_path = os.path.expanduser('~/.ssh/known_hosts')
        try:
            ssh.load_host_keys(known_hosts_path)
        except Exception as ex:
            print("Error loading known_hosts file!")
            err_str = "Error loading known_hosts file: " + known_hosts_path
            return None, err_str

        try:
            # Connect to the server
            ssh.connect(ssh_server, username=ssh_user,
                        password=ssh_pass, compress=True, look_for_keys=False, timeout=5)
            # Make sure we are added to the authorized keys
            add_ssh_key_to_authorized_keys(ssh)
        except paramiko.ssh_exception.BadHostKeyException:
            print("Invalid Host key!")
            err_str = "Invalid Host Key"
            ssh = None
            # error_message.text = "\n\n[b]CONNECTION ERROR[/b]\n - Bad host key - check ~/.ssh/known_hosts"
            # fog_image_upload_send_button.disabled = False
            pass
        except paramiko.ssh_exception.BadAuthenticationType:
            # error_message.text = "[b]INVALID LOGIN[/b]"
            # fog_image_upload_send_button.disabled = False
            print("Invalid Login!")
            err_str = "Invalid Login!"
            ssh = None
            pass
        except paramiko.SSHException as ex:
            print("Error connecting to SSH server - check IP of the ssh server " + str(ssh_server))
            err_str = "Error connecting to SSH server - " + str(ssh_server)
            ssh = None
        except socket.timeout:
            print("Error connecing to SSH server - timeout trying to connect, check the IP of the server " + str(ssh_server))
            err_str = "Timeout error connecting to SSH server - " + str(ssh_server)
            ssh = None
        except socket.error as ex:
            print("Error connecting to SSH server - check IP of the ssh server " + str(ssh_server))
            err_str = "Error connecting to SSH server - " + str(ssh_server)
            ssh = None
        except Exception as ex:
            try:
                if 'Bad authentication type' in ex:
                #    self.log_text_to_label(status_label, "\n[b]INVALID LOGIN[/b]")
                    pass
            except:
                # If not iterable, it is ok - timeout error won't be iterable
                #self.log_text_to_label(status_label, "\n[b]CONNECTION ERROR[/b]\n" + str(ex))
                pass
    
            print("Unknown ERROR! " + str(ex))
            err_str = "Unknown Error! " + str(ex)
            ssh = None
            # error_message.text = "[b]Unknown ERROR[/b]\n" + str(ex)
            # fog_image_upload_send_button.disabled = False
            pass
        
    else:
        # Bad or missing login info?
        err_str = "Missing username or password!"
        ssh = None
    
    return (ssh, err_str)

def remove_server_from_known_hosts(ssh_server):
    # Remove this server from the known_hosts file so that it doesn't
    # blow up if the IP used to belong to another server
    # NOTE - YES - this is abusing SSH keys a little, practicle issues
    # mean this keeps creeping up when people migrate servers though causing
    # tech support calls
    # Get project folder (parent folder)
    root_path = os.path.dirname(get_app_folder())
    # Make sure ssh keys exist (saved in home directory in .ssh folder on current computer)
    bash_path = os.path.join(root_path, "bin/bin/bash.exe")
    # Run this to generate keys
    proc = subprocess.Popen(bash_path + " -c 'ssh-keygen -R \"" + ssh_server + "\"", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        # proc.stdin.write("\n\n")  #  Write 2 line feeds to add empty passphrase
        pass
    except:
        # This will fail if it isn't waiting for input, that is ok
        pass
    proc.stdin.close()
    for line in proc.stdout:
        pass
        # self.log_text_to_label(status_label, line)
    #  ret += proc.stdout.read().decode('utf-8')

def generate_local_ssh_key():
    # Make sure the .ssh folder exists
    known_hosts_path = os.path.expanduser('~/.ssh')
    if not os.path.exists(known_hosts_path):
        os.makedirs(known_hosts_path, exist_ok=True)

    # Make sure the known_hosts file exists
    known_hosts_path = os.path.join(known_hosts_path, "known_hosts")
    if not os.path.exists(known_hosts_path):
        try:
            f = open(known_hosts_path, "a")
            f.close()
        except Exception as ex:
            print("Error creating known_hosts file: " + known_hosts_path)
            err_str = "Error creating known_hosts file: " + known_hosts_path
            return None, err_str

    # Get project folder (parent folder)
    root_path = os.path.dirname(get_app_folder())
    # Make sure ssh keys exist (saved in home directory in .ssh folder on current computer)
    bash_path = os.path.join(root_path, "bin/bin/bash.exe")
    # Run this to generate keys
    proc = subprocess.Popen(bash_path + " -c 'if [ ! -f ~/.ssh/id_rsa ]; then ssh-keygen -P \"\" -t rsa -f ~/.ssh/id_rsa; fi'", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    try:
        # proc.stdin.write("\n\n")  #  Write 2 line feeds to add empty passphrase
        pass
    except:
        # This will fail if it isn't waiting for input, that is ok
        pass
    proc.stdin.close()
    for line in proc.stdout:
        pass
        # self.log_text_to_label(status_label, line)
    #  ret += proc.stdout.read().decode('utf-8')

def add_ssh_key_to_authorized_keys(ssh):
    ret = ""

    # Get project folder (parent folder)
    root_path = os.path.dirname(get_app_folder())
    # Make sure ssh keys exist (saved in home directory in .ssh folder on current computer)
    bash_path = os.path.join(root_path, "bin/bin/bash.exe")

    # Make sure remote server has .ssh folder
    stdin, stdout, stderr = ssh.exec_command("mkdir -p ~/.ssh; chmod 700 ~/.ssh;", get_pty=True)
    stdin.close()
    for line in stdout:
        pass
        # self.log_text_to_label(status_label, line)

    # Find the server home folder
    stdin, stdout, stderr = ssh.exec_command("cd ~; pwd;", get_pty=True)
    stdin.close()
    server_home_dir = stdout.read().decode('utf-8')
    if server_home_dir is None:
        server_home_dir = ""
    server_home_dir = server_home_dir.strip()

    # Add ssh keys to server for easy push/pull later
    # bash -- cygpath -w ~   to get win version of home directory path
    proc = subprocess.Popen(bash_path + " -c 'cygpath -w ~'", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    proc.stdin.close()
    home_folder = proc.stdout.read().decode('utf-8').strip()
    # home_folder = get_home_folder() #  expanduser("~")
    rsa_pub_path = os.path.join(home_folder, ".ssh", "id_rsa.pub")
    sftp = ssh.open_sftp()
    sftp.put(rsa_pub_path, os.path.join(server_home_dir, ".ssh/id_rsa.pub.ope").replace("\\", "/"))
    sftp.close()
    # Make sure we remove old entries
    stdin, stdout, stderr = ssh.exec_command("awk '{print $3}' ~/.ssh/id_rsa.pub.ope", get_pty=True)
    stdin.close()
    remove_host = stdout.read().decode('utf-8')
    # Add if/then to command to prevent error when authorized_keys file doesn't exist
    stdin, stdout, stderr = ssh.exec_command("if [ -f ~/.ssh/authorized_keys ]; then sed -i '/" + remove_host.strip() + "/d' ~/.ssh/authorized_keys; fi", get_pty=True)
    stdin.close()
    for line in stdout:
        # self.log_text_to_label(status_label, line)
        pass

    # Add id_rsa.pub.ope to the authorized_keys file
    stdin, stdout, stderr = ssh.exec_command("cat ~/.ssh/id_rsa.pub.ope >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys;", get_pty=True)
    stdin.close()
    for line in stdout:
        # self.log_text_to_label(status_label, line)
        pass

    # Should be automatic now - known_hosts loaded in connect function
    # Last step - make sure that servers key is accepted here so we don't get warnings
    #known_hosts_path = os.path.join(home_folder, ".ssh", "known_hosts" )
    #ssh.save_host_keys(known_hosts_path)

    return ret


def quote_argument(argument):
    return '"%s"' % (
        argument
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        .replace('$', '\\$')
        .replace('`', '\\`')
    )

# Custom FileChooser File System - for SFTP image folders
class FogSFTPFileSystem(FileSystemAbstract):
    def __init__(self, ssh_server="", ssh_user="", ssh_pass="", ssh_folder=""):
        # Pull a list of images from the online or offline server.
        self.ssh_server = ssh_server
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_folder = ssh_folder
        self.file_list = dict()
        self.pullimagelist()

    def pullimagelist(self):
        # self.server_mode = SyncOPEApp.server_mode
        # print("server mode " + self.server_mode)

        # Reset file list
        self.file_list = dict()

        if self.ssh_server != "" and self.ssh_user != "" and self.ssh_pass != "" and self.ssh_folder != "":
            # Connect to server
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                # Connect to the server
                ssh.connect(self.ssh_server, username=self.ssh_user,
                            password=self.ssh_pass, compress=True, look_for_keys=False, timeout=3)

                # remote path
                remote_images_path = os.path.join(self.ssh_folder, "volumes/fog/images").replace("\\", "/")
                # Use DU command to pull the whole list quickly
                cmd = "du -sb " + remote_images_path + "/*/"

                stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
                stdin.close()
                for line in stdout:
                    parts = line.split("\t")
                    dsize = int(parts[0].strip())
                    dname = os.path.basename(parts[1].strip().strip("/"))
                    if dname != "dev":
                        self.file_list[dname] = dsize
                ssh.close()
            except paramiko.ssh_exception.BadHostKeyException:
                print("Invalid Host key!")
                # error_message.text = "\n\n[b]CONNECTION ERROR[/b]\n - Bad host key - check ~/.ssh/known_hosts"
                # fog_image_upload_send_button.disabled = False
                pass
            except paramiko.ssh_exception.BadAuthenticationType:
                # error_message.text = "[b]INVALID LOGIN[/b]"
                # fog_image_upload_send_button.disabled = False
                print("Invalid Login!")
                pass
            except Exception as ex:
                print("Unknown ERROR!")
                # error_message.text = "[b]Unknown ERROR[/b]\n" + str(ex)
                # fog_image_upload_send_button.disabled = False
                pass

        # Need an empty place holder if nothing is there
        if len(self.file_list) < 1:
            self.file_list['no images available'] = 0

        return

    def listdir(self, fn):
        # print("getting files " + str(self.file_list.keys()))
        return self.file_list.keys()

    def getsize(self, fn):
        ret = 0
        # has a leading \ ??
        file_name = fn.strip("\\")
        # print("looking for size of " + str(file_name))
        if file_name in self.file_list.keys():
            # print("found file size " + str(file_name))
            ret = self.file_list[file_name]
        return ret

    def is_hidden(self, fn):
        return False

    def is_dir(self, fn):
        return False


# Custom FileChooser File System - Pull list from HTTP download page
class FogDownloadFileSystem(FileSystemAbstract):
    def __init__(self, parent_app, initial=False):
        self.parent_app = parent_app
        self.file_list = dict()

        if initial is True:
            self.file_list['Press refresh to pull list when online'] = 0
        else:
            #self.getwebdir(SyncOPEApp.ope_fog_images_url)
            self.getwebdir(parent_app.ope_fog_images_url)

    def getwebdir(self, url):
        # Pull the URL

        self.file_list = dict()
        if self.parent_app.is_online() is not True:
            # Need an empty place holder if nothing is there
            if len(self.file_list) < 1:
                self.file_list['no images available in offline mode'] = 0
            return

        try:
            response = requests.get(url)

            if not response.ok:
                logging.warn("ERROR pulling list of fog images from OPE server " + url)
            else:
                # Parse the html for links and file sizes
                html = response.text

                matches = re.findall(r'a href=[\'"]?([^\'" >]+)[\'"]>.*</a></td><td[^\>]*>([^<]+)</td><td[^\>]*>([^<]+)</td>', html)
                for item in matches:
                    # Skip / entry
                    if item[0] != "/":
                        # Figure out real size in bytes
                        s = self.parsesizeinbytes(item[2])
                        self.file_list[item[0]] = s

        except Exception as ex:
            logging.info("Not able to connect to " + str(url) + " to pull list of fog images")

        # Need an empty place holder if nothing is there
        if len(self.file_list) < 1:
            self.file_list['no images available'] = 0

        return

    def parsesizeinbytes(self, size):
        # Comes in with a size like 100M which needs to be converted to bytes
        ret = 0
        matches = re.search("(\d)+", size)
        if matches.group(0):
            ret = int(matches.group(0))

        # Pick out the letter
        if 'M' in size.upper():
            ret = ret * 1024 * 1024
        if 'K' in size.upper():
            ret = ret * 1024
        if 'G' in size.upper():
            ret = ret * 1024 * 1024 * 1024

        return ret

    def listdir(self, fn):
        # print("getting files " + str(self.file_list.keys()))
        return self.file_list.keys()

    def getsize(self, fn):
        ret = 0
        # has a leading \ ??
        file_name = fn.strip("\\")
        # print("looking for size of " + str(file_name))
        if file_name in self.file_list.keys():
            # print("found file size " + str(file_name))
            ret = self.file_list[file_name]
        return ret

    def is_hidden(self, fn):
        return False

    def is_dir(self, fn):
        return False


