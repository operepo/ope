import paramiko
import os
import sys
import requests
import threading
from threading import Thread
import time
import getpass
import color
# from color import p

from kivy.clock import mainthread

# Class to detect and manage secure sync boxes
class SyncBoxes:
    # How long to wait on a connection attempt to find a sync box
    FIND_SYNC_BOX_TIMEOUT = 3.0

    def __init__(self, router_files_folder=None, router_user="admin", router_pw=None,
                 output_label=None):

        if router_files_folder is None:
            raise Exception("Invalid router files folder!")

        self.router_user = router_user
        self.router_pw = router_pw
        self.output_label = output_label

        self.detected_routers = []
        self.router_log = []

        # Determine if the thread is running for finding hosts
        self.find_thread_running = False
        self.find_threads = []

        # Monitor router update process
        self.update_router_thread_running = False
        self.update_router_threads = []

        self.router_files_folder = router_files_folder
        self.find_subnet_prefix = None

    @mainthread
    def set_text_property(self, label_control, text, clear_previous_text=False):
        # Do this in the main thread so that it doesn't mess with kivy
        if label_control is not None:
            if clear_previous_text is True:
                label_control.text = text
            else:
                label_control.text += text
        else:
            print("Skipping log - label_control is none!")
    
    def p(self, msg="", end=True, out=None, debug_level=0):
        if self.output_label is None:
            color.p(msg, end=end, out=out, debug_level=debug_level)
            return

        # Convert color codes?
        msg = color.translate_color_codes_to_markup(msg)

        if end is True:
            end = "\n"
        # Print to the label
        self.set_text_property(self.output_label, msg + end)
        #self.output_label.text += msg + end

    def find_routers(self, subnet_prefix=None):
        # Find routers on this subnet
        if self.find_thread_running is True:
            self.p("}}rbFind Sync Box thread already running...}}xx")
            return

        self.find_subnet_prefix = subnet_prefix

        self.find_thread_running = True
        self.find_threads = []

        # TODO - Currently assumes 24 bit subnet - so only scans 0-255, expand code to deal with larger subnets
        for i in range(1, 254):
            ip = self.find_subnet_prefix.strip(".")
            ip = ip + "." + str(i)
            # print("Starting find thread for " + ip)
            t = Thread(target=self.find_sync_box_thread, args=(ip,))
            self.find_threads.append(t)
            t.start()

        # Wait on threads to finish
        while len(self.find_threads) > 0:
            # print("\r Waiting for find threads to exit..." + str(len(self.find_threads)))

            # Slight wait for threads...
            time.sleep(0.1)

        self.p("}}gnDone searching for Sync Boxes!}}xx")
        self.find_thread_running = False

        pass

    def find_sync_box_thread(self, ip=None):
        # Thread to bounce request off ip to see if it is a router
        if ip is None:
            # Invalid IP
            self.p("}}rbInvalid IP for find sync box thread: None}}xx")
            self.find_threads.remove(threading.current_thread())
            return

        if self.is_router(ip) is True:
            # Found Router OS.
            self.p("}}gbFound RouterOS Device at " + str(ip) + "}}xx")
            self.detected_routers.append(ip)
        else:
            # print(str(ip) + " is not a RouterOS device")
            pass

        # When done, remove itself from the list of threads

        self.find_threads.remove(threading.current_thread())
        return

    def is_router(self, router_ip=None):
        # Do a port 80 check to see if this is a RouterOS device by finding "RouterOS" in the text
        if router_ip is None:
            return False

        router_ip = router_ip.lower().replace("https://", "").replace("http://", "")
        router_ip = "http://" + router_ip

        try:
            resp = requests.get(router_ip, timeout=SyncBoxes.FIND_SYNC_BOX_TIMEOUT)

            if resp.ok:
                html = resp.text
                if html.find("RouterOS") > -1:
                    self.router_log.append("Found RouterOS at " + str(router_ip))
                    return True
                else:
                    return False
        except requests.exceptions.ConnectTimeout:
            # self.p("Timeout waiting for connection " + str(router_ip))
            pass
        except requests.exceptions.SSLError:
            # self.p("SSL error - moving on " + str(router_ip))
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception as ex:
            self.p("}}rbUnknown Error getting info from ip " + str(router_ip) + " " + str(ex) + "}}xx")
        return False

    def update_routers(self, router_list=None):
        if self.update_router_thread_running is True:
            self.p("}}rbUpdate thread already running...}}xx")
            return

        self.update_router_thread_running = True
        r_list = router_list
        if r_list is None:
            # No list provided, use the detected routers list
            r_list = self.detected_routers

        for r in r_list:
            # Run a thread for each router ip to try and update it
            t = Thread(target=self.update_router_thread, args=(r,))
            self.update_router_threads.append(t)
            t.start()

        # Wait for threads to finish...
        while len(self.update_router_threads) > 0:
            self.p(".", end="")
            time.sleep(0.5)

        self.p("}}ybAll routers finished updating...}}xx")
        self.update_router_thread_running = False

    def update_router_thread(self, router_ip=None):
        # Thread to apply updates to a single router
        if router_ip is None:
            self.p("}}rbInvalid router ip! None}}xx")
            self.update_router_threads.remove(threading.current_thread())
            return

        if self.update_router(router_ip) is True:
            self.p("}}gnRouter updated " + str(router_ip) + "}}xx")
        else:
            self.p("}}rbError updating router " + str(router_ip) + "}}xx")

        self.update_router_threads.remove(threading.current_thread())
        return

    def update_router(self, router_ip=None):
        # SSH in and copy packages
        # https://wiki.mikrotik.com/wiki/Manual:Upgrading_RouterOS
        # # Auto update process
        # - use SCP Push NPK files for os and plugins to root folder
        # - Reboot to make it auto upgrade ( system reboot )
        # - Do firmware upgrade after reboot ( system routerboard upgrade )

        # Try and connect - use pw, and if that fails try admin w no pw (new router)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try_no_pw = False
        pw_used = ""
        backup_file = "ope-backup.backup"

        try:
            ssh.connect(router_ip, username=self.router_user,
                        password=self.router_pw, compress=True, look_for_keys=False)
            try_no_pw = False
            pw_used = self.router_pw
        except paramiko.ssh_exception.BadHostKeyException:
            self.p("}}rbUpdate Router Connect - Invalid Host key! - check known_hosts file ~/.ssh/known_hosts}}xx")
            return False
        except paramiko.ssh_exception.BadAuthenticationType:
            # Try again w no pw
            try_no_pw = True
        except Exception as ex:
            self.p("}}rbUpdate Router Connect - Unknown Error! " + str(ex) + "}}xx")
            return False

        if try_no_pw:
            try:
                self.p("}}mb---- Trying 2nd connection w/out password for new router ----}}xx")
                ssh.connect(router_ip, username=self.router_user,
                            password="", compress=True, look_for_keys=False)
                pw_used = ""
            except Exception as ex:
                self.p("}}rbUpdate Router Connect No PW - Error Connecting " + str(ex) + "}}xx")
                return False

        # Should have good SSH object now. Open SCP object and push NPK files
        sftp = ssh.open_sftp()

        # Get list of files to push
        fpath = self.router_files_folder
        for root, dirs, files in os.walk(fpath, topdown=False):
            for f in files:
                if f.lower().endswith(".npk") or f.lower().endswith(".backup"):
                    if f.lower().endswith(".backup"):
                        backup_file = f
                    # Push this file
                    self.p("}}mb --> Pushing " + f + "}}xx")
                    fp = os.path.join(fpath, f)
                    try:
                        sftp.put(fp, f, confirm=True)
                    except Exception as ex:
                        self.p("}}rbERROR pushing update files to " + router_ip + " (" + f + ") " + str(ex) + "}}xx")
                        sftp.close()
                        ssh.close()
                        return False
                else:
                    self.p("}}yb -- Not an NPK or backup file - skipping " + f + "}}xx")
                    pass

        sftp.close()
        self.p("}}ybDone pushing files to " + router_ip + "}}xx")

        self.p("\n}}ybRebooting Router to trigger update..." + router_ip + "}}xx")
        cmd = "system reboot"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        exit_status = stdout.channel.recv_exit_status()
        for line in stdout.readlines():
            self.p("}}cnRouter Output: " + router_ip + ": " + line + "}}xx", debug_level=3)
            # make sure to read all lines, even if we don't print them
            pass
        ssh.close()

        # Wait for reboot....
        self.p("\n}}ybWaiting for reboot (about 90 seconds)...}}xx")
        wait_time = 90
        start_wait = time.time()
        while time.time() - wait_time < start_wait:
            time.sleep(0.5)

        # Try to connect for a bit
        start_connect_time = time.time()
        connected = False
        self.p("\n}}ybTrying to reconnect...}}xx")
        while connected is False:
            if time.time() - 120 > start_connect_time:
                # Taking way too long
                self.p("}}rbUpdate Router - Taking WAY too long to reboot after update " + router_ip + "}}xx")
                return False

            try:
                ssh.connect(router_ip, username=self.router_user, password=pw_used,
                            compress=True, look_for_keys=False)
                connected = True
            except:
                # Keep trying to connect
                pass
            time.sleep(0.3)

        self.p("\n}}ybCleaning up NPK files " + router_ip + "}}xx")
        sftp = ssh.open_sftp()
        sftp_files = sftp.listdir()
        for f in sftp_files:
            if f.lower().endswith(".npk"):
                self.p("}}mb - Removing NPK file " + f + "}}xx")
                sftp.remove(f)
        sftp.close()

        self.p("\n}}ybRunning firmware update " + router_ip + "}}xx")
        cmd = "system routerboard upgrade"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        # exit_status = stdout.channel.recv_exit_status()
        # for line in stdout.readlines():
        #    self.p("Router Output: " + router_ip + ": " + line)
        #    # make sure to read all lines, even if we don't print them
        #    pass
        time.sleep(5)

        # Reboot again...
        cmd = "system reboot"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        # exit_status = stdout.channel.recv_exit_status()
        # for line in stdout.readlines():
        #    self.p("Router Output: " + router_ip + ": " + line)
        #    # make sure to read all lines, even if we don't print them
        #    pass
        time.sleep(5)

        ssh.close()

        self.p("\n}}ybRebooting again to apply firmware update (about 90 seconds) " + router_ip + "}}xx")
        wait_time = 90
        start_wait = time.time()
        while time.time() - wait_time < start_wait:
            time.sleep(0.5)

        # Try to connect for a bit
        start_connect_time = time.time()
        connected = False
        self.p("\n}}ybTrying to reconnect...}}xx")
        while connected is False:
            if time.time() - 120 > start_connect_time:
                # Taking way too long
                self.p("}}rbUpdate Router - Taking WAY too long to reboot after update " + router_ip + "}}xx")
                return False

            try:
                ssh.connect(router_ip, username=self.router_user, password=pw_used,
                            compress=True, look_for_keys=False)
                connected = True
            except:
                # Keep trying to connect
                pass
            time.sleep(0.3)

        # Time to restore configuration for the router
        self.p("\n}}ybApplying router configuration " + router_ip + "}}xx")

        # SSH in and copy config and update router
        # https://wiki.mikrotik.com/wiki/Manual:Configuration_Management#Importing_Configuration
        # # Push updated configs
        # - Use SCP to push backup file to root folder
        # - Restore backup file with ( system backup load name=backupfile )
        # - Backup file ( system backup save name=backupfile )
        cmd = "system backup load name=" + backup_file + " password=\"" + self.router_pw + "\""
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        # TODO TODO - Final restore not working on a new box, needs decrypt pw and error checking
        # exit_status = stdout.channel.recv_exit_status()
        # for line in stdout.readlines():
        #    print("Router Output: " + router_ip + ": " + line)
        #    # make sure to read all lines, even if we don't print them
        #    pass
        time.sleep(5)

        ssh.close()

        self.p("\n}}gbFinal reboot started - configuration applied! After reboot the device should be ready to use.}}xx")
        self.p("Router should be done rebooting in about 120 seconds.")

        return True


if __name__ == "__main__":
    # Ask for subnet prefix
    color.p("}}yb----- NEW SYNC BOX SETUP -----}}xx")
    color.p("Plug into a port (NOT PORT 1) or USB cable if it is in a box and use subnet 192.168.88")
    color.p("}}yb----- UPDATE EXISTING SYNC BOX -----}}xx")
    color.p("}}mb--- Directly from the sync box ---}}xx")
    color.p("Plugin to a USB cable and use subnet 202.5.222")
    color.p("}}mb--- From PC connected to the network ---}}xx")
    color.p("Use your DHCP network subnet (e.g. ours is 172.20.31)")
    color.p("")
    sn_prefix = input("Please enter subnet to scan [enter for new box on 192.168.88]:")
    if sn_prefix.strip() == "":
        sn_prefix = "192.168.88"

    pw = getpass.getpass("Enter router pw: ")

    color.p("}}mbFinding routers...}}xx")

    app_folder = ""
    if getattr(sys, 'frozen', False):
        # Running in pyinstaller bundle
        app_folder = sys._MEIPASS
    else:
        # Running as normal script
        app_folder = os.path.dirname(os.path.abspath(__file__))

    # Grab from ../router_files folder
    router_files_path = os.path.join(os.path.dirname(app_folder), "router_files")
    color.p("}}cnPackage Folder: " + router_files_path + "}}xx")
    sys.exit()

    sb = SyncBoxes(router_files_folder=router_files_path, router_pw=pw)

    sb.find_routers(subnet_prefix=sn_prefix)
    sb.update_routers()

    color.p("}}gbUpdate Done!}}xx")


