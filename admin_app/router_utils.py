import paramiko
import os
import requests
import threading
from threading import Thread
import time
import getpass
import color
from color import p


# Class to detect and manage secure sync boxes
class SyncBoxes:
    # How long to wait on a connection attempt to find a sync box
    FIND_SYNC_BOX_TIMEOUT = 3.0

    def __init__(self, router_files_folder=None, router_user="admin", router_pw=None):

        if router_files_folder is None:
            raise Exception("Invalid router files folder!")

        self.router_user = router_user
        self.router_pw = router_pw

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

    def find_routers(self, subnet_prefix=None):
        # Find routers on this subnet
        if self.find_thread_running is True:
            p("}}rbFind Sync Box thread already running...}}xx")
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

        p("}}gnDone searching for Sync Boxes!}}xx")
        self.find_thread_running = False

        pass

    def find_sync_box_thread(self, ip=None):
        # Thread to bounce request off ip to see if it is a router
        if ip is None:
            # Invalid IP
            p("}}rbInvalid IP for find sync box thread: None}}xx")
            self.find_threads.remove(threading.current_thread())
            return

        if self.is_router(ip) is True:
            # Found Router OS.
            p("}}gbFound RouterOS Device at " + str(ip) + "}}xx")
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
            # print("Timeout waiting for connection " + str(router_ip))
            pass
        except requests.exceptions.SSLError:
            # print("SSL error - moving on " + str(router_ip))
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception as ex:
            p("}}rbUnknown Error getting info from ip " + str(router_ip) + " " + str(ex) + "}}xx")
        return False

    def update_routers(self, router_list=None):
        if self.update_router_thread_running is True:
            p("}}rbUpdate thread already running...}}xx")
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
            print(".", end="")
            time.sleep(0.5)

        p("}}ybAll routers finished updating...}}xx")
        self.update_router_thread_running = False

    def update_router_thread(self, router_ip=None):
        # Thread to apply updates to a single router
        if router_ip is None:
            p("}}rbInvalid router ip! None}}xx")
            self.update_router_threads.remove(threading.current_thread())
            return

        if self.update_router(router_ip) is True:
            p("}}gnRouter updated " + str(router_ip) + "}}xx")
        else:
            p("}}rbError updating router " + str(router_ip) + "}}xx")

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
            p("}}rbUpdate Router Connect - Invalid Host key! - check known_hosts file ~/.ssh/known_hosts}}xx")
            return False
        except paramiko.ssh_exception.BadAuthenticationType:
            # Try again w no pw
            try_no_pw = True
        except Exception as ex:
            p("}}rbUpdate Router Connect - Unknown Error! " + str(ex) + "}}xx")
            return False

        if try_no_pw:
            try:
                p("}}mb---- Trying 2nd connection w/out password for new router ----}}xx")
                ssh.connect(router_ip, username=self.router_user,
                            password="", compress=True, look_for_keys=False)
                pw_used = ""
            except Exception as ex:
                p("}}rbUpdate Router Connect No PW - Error Connecting " + str(ex) + "}}xx")
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
                    p("}}mb --> Pushing " + f + "}}xx")
                    fp = os.path.join(fpath, f)
                    try:
                        sftp.put(fp, f, confirm=True)
                    except Exception as ex:
                        p("}}rbERROR pushing update files to " + router_ip + " (" + f + ") " + str(ex) + "}}xx")
                        sftp.close()
                        ssh.close()
                        return False
                else:
                    p("}}yb -- Not an NPK or backup file - skipping " + f + "}}xx")
                    pass

        sftp.close()
        p("}}ybDone pushing files to " + router_ip + "}}xx")

        p("\n}}ybRebooting Router to trigger update..." + router_ip + "}}xx")
        cmd = "system reboot"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        exit_status = stdout.channel.recv_exit_status()
        for line in stdout.readlines():
            p("}}cnRouter Output: " + router_ip + ": " + line + "}}xx", debug_level=3)
            # make sure to read all lines, even if we don't print them
            pass
        ssh.close()

        # Wait for reboot....
        p("\n}}ybWaiting for reboot...}}xx")
        wait_time = 90
        start_wait = time.time()
        while time.time() - wait_time < start_wait:
            time.sleep(0.5)

        # Try to connect for a bit
        start_connect_time = time.time()
        connected = False
        p("\n}}ybTrying to reconnect...}}xx")
        while connected is False:
            if time.time() - 120 > start_connect_time:
                # Taking way too long
                p("}}rbUpdate Router - Taking WAY too long to reboot after update " + router_ip + "}}xx")
                return False

            try:
                ssh.connect(router_ip, username=self.router_user, password=pw_used,
                            compress=True, look_for_keys=False)
                connected = True
            except:
                # Keep trying to connect
                pass
            time.sleep(0.3)

        p("\n}}ybCleaning up NPK files " + router_ip + "}}xx")
        sftp = ssh.open_sftp()
        sftp_files = sftp.listdir()
        for f in sftp_files:
            if f.lower().endswith(".npk"):
                p("}}mb - Removing NPK file " + f + "}}xx")
                sftp.remove(f)
        sftp.close()

        p("\n}}ybRunning firmware update " + router_ip + "}}xx")
        cmd = "system routerboard upgrade"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        # exit_status = stdout.channel.recv_exit_status()
        # for line in stdout.readlines():
        #    print("Router Output: " + router_ip + ": " + line)
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
        #    print("Router Output: " + router_ip + ": " + line)
        #    # make sure to read all lines, even if we don't print them
        #    pass
        time.sleep(5)

        ssh.close()

        p("\n}}ybRebooting again to apply firmware update " + router_ip + "}}xx")
        wait_time = 90
        start_wait = time.time()
        while time.time() - wait_time < start_wait:
            time.sleep(0.5)

        # Try to connect for a bit
        start_connect_time = time.time()
        connected = False
        p("\n}}ybTrying to reconnect...}}xx")
        while connected is False:
            if time.time() - 120 > start_connect_time:
                # Taking way too long
                p("}}rbUpdate Router - Taking WAY too long to reboot after update " + router_ip + "}}xx")
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
        p("\n}}ybApplying router configuration " + router_ip + "}}xx")

        # SSH in and copy config and update router
        # https://wiki.mikrotik.com/wiki/Manual:Configuration_Management#Importing_Configuration
        # # Push updated configs
        # - Use SCP to push backup file to root folder
        # - Restore backup file with ( system backup load name=backupfile )
        # - Backup file ( system backup save name=backupfile )
        p("\n}}ybRunning firmware update " + router_ip + "}}xx")
        cmd = "system backup load name=" + backup_file + " password=\"" + self.router_pw + "\""
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        time.sleep(0.5)
        stdin.write("y\n")
        time.sleep(0.5)
        stdin.close()
        # exit_status = stdout.channel.recv_exit_status()
        # for line in stdout.readlines():
        #    print("Router Output: " + router_ip + ": " + line)
        #    # make sure to read all lines, even if we don't print them
        #    pass
        time.sleep(5)

        ssh.close()

        p("\n}}gbFinal reboot started - configuration applied! After reboot the device should be ready to use.}}xx")

        return True


if __name__ == "__main__":
    # Ask for subnet prefix
    p("}}yb----- NEW SYNC BOX SETUP -----}}xx")
    p("Plug into a port (NOT PORT 1) or USB cable if it is in a box and use subnet 192.168.88")
    p("}}yb----- UPDATE EXISTING SYNC BOX -----}}xx")
    p("}}mb--- Directly from the sync box ---}}xx")
    p("Plugin to a USB cable and use subnet 202.5.222")
    p("}}mb--- From PC connected to the network ---}}xx")
    p("Use your DHCP network subnet (e.g. ours is 172.20.31)")
    p("")
    sn_prefix = input("Please enter subnet to scan [enter for new box on 192.168.88]:")
    if sn_prefix.strip() == "":
        sn_prefix = "192.168.88"

    pw = getpass.getpass("Enter router pw: ")

    p("}}mbFinding routers...}}xx")
    router_files_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "router_files")
    p("}}cnPackage Folder: " + router_files_path + "}}xx")

    sb = SyncBoxes(router_files_folder=router_files_path, router_pw=pw)

    sb.find_routers(subnet_prefix=sn_prefix)
    sb.update_routers()

    p("}}gbUpdate Done!}}xx")


