import getpass
import json
import os
import sys
import time
import subprocess

from mgmt_FolderPermissions import FolderPermissions
from mgmt_RegistrySettings import RegistrySettings
from mgmt_UserAccounts import UserAccounts
from mgmt_RestClient import RestClient
from mgmt_Computer import Computer
from mgmt_GroupPolicy import GroupPolicy
from mgmt_ProcessManagement import ProcessManagement
from mgmt_SystemTime import SystemTime


from color import p
import util


class CredentialProcess:
    COMPUTER_INFO = None

    @staticmethod
    def get_mgmt_version(version_file=None):
        ret = "NO VERSION"

        # Try to load the version file
        if version_file is None:
            app_folder = util.get_app_folder()
            version_file = os.path.join(app_folder, "mgmt.version")
        
        if os.path.exists(version_file):
            try:
                f = open(version_file, "r")
                ver = json.load(f)
                f.close()
                ret = ver["version"]
            except Exception as ex:
                p("}}rbError reading mgmt.version!}}xx\n" + str(ex))

        else:
            p("}}rnNo mgmt.version file exists!")

        return ret

    @staticmethod
    def get_credentialed_student():
        # Return the name of the current credentialed student or None if missing
        return RegistrySettings.get_reg_value(value_name="student_user", default=None)
    
    @staticmethod
    def get_credentialed_admin():
        # Return the name of the current credentialed student or None if missing
        return RegistrySettings.get_reg_value(app="OPEService", value_name="admin_user", default=None)
        
    @staticmethod
    def credential_input_verify_loop():
        # Loop until we quit or get good stuff

        # Return a list of values
        # student_full_name, laptop_admin_user, laptop_admin_password
        ret = []

        mgmt_version = CredentialProcess.get_mgmt_version()

        smc_url = RegistrySettings.get_reg_value(value_name="smc_url", default="https://smc.ed")
        canvas_url = ""
        canvas_access_token = ""
        student_user = RegistrySettings.get_reg_value(value_name="student_user")
        student_full_name = ""
        student_password = ""
        smc_admin_user = RegistrySettings.get_reg_value(app="OPEService", value_name="smc_admin_user", default="admin")
        smc_admin_password = ""

        laptop_admin_user = ""
        laptop_admin_password = ""

        loop_running = True
        while loop_running:
            p("\n}}gb Version: " + mgmt_version + "}}xx")
            
            p("""

}}mn======================================================================
}}mn| }}ybOPE Credential App                                                 }}mn|
}}mn| }}xxThis app will add student credentials to the computer and          }}mn|
}}mn| }}xxsecure the laptop for inmate use.                                  }}mn|
}}mn| }}yn(answer with quit to stop this tool)                               }}mn|
}}mn======================================================================}}xx

            """)

            # 4 - Ask for input (smc server, login, student name, etc...)
            p("}}ynEnter URL for SMC Server }}cn[enter for " + smc_url + "]:}}xx ", False)
            tmp = input()
            tmp = tmp.strip()
            if tmp.lower() == "quit":
                p("}}rnGot QUIT - exiting credential!}}xx")
                return None
            if tmp == "":
                tmp = smc_url
            smc_url = tmp
            # Make sure url has https or http in it
            if "https://" not in smc_url.lower() and "http://" not in smc_url.lower():
                smc_url = "https://" + smc_url

            p("}}ynPlease enter the ADMIN user name }}cn[enter for " + smc_admin_user + "]:}}xx ", False)
            tmp = input()
            tmp = tmp.strip()
            if tmp.lower() == "quit":
                p("}}rnGot QUIT - exiting credential!}}xx")
                return None
            if tmp == "":
                tmp = smc_admin_user
            smc_admin_user = tmp

            p("}}ynPlease enter ADMIN password }}cn[characters will not show]:}}xx", False)
            tmp = getpass.getpass(" ")
            if tmp.lower() == "quit":
                p("}}rnGot QUIT - exiting credential!}}xx")
                return None
            if tmp == "":
                p("}}rbA password is required.}}xx")
                continue
            smc_admin_password = tmp

            tmp = ""
            last_student_user_prompt = ""
            while tmp.strip() == "":
                if student_user != "":
                    last_student_user_prompt = " }}cn[enter for previous student " + student_user + "]"
                    # p("}}mb\t- Found previously credentialed user: }}xx" + str(last_student_user))
                p("}}ynPlease enter the username for the student" + last_student_user_prompt + ":}}xx ", False)
                tmp = input()
                if tmp.lower() == "quit":
                    p("}}rnGot QUIT - exiting credential!}}xx")
                    return None
                if tmp.strip() == "":
                    tmp = student_user
            student_user = tmp.strip()

            # - Bounce off SMC - verify_ope_account_in_smc
            try:
                result = RestClient.verify_ope_account_in_smc(student_user, smc_url, smc_admin_user, smc_admin_password)
                if result is None:
                    # Should show errors during the rest call, so none here
                    #p("}}rbUnable to validate student against SMC!}}xx")
                    # Jump to top of loop and try again
                    continue
                    #return False # sys.exit(-1)
            except Exception as ex:
                p("}}rbError - Unable to verify student in SMC}}xx\n" + str(ex))
                # Jump to top of loop and try again
                continue
            
            # If not None - result will be a tuple of information
            laptop_admin_user, student_full_name, smc_version = result
            
            # Verify that the info is correct
            txt = """
}}mn======================================================================
}}mn| }}gbFound Student - Continue?                                          }}mn|
}}mn| }}ynCredential Version:    }}cn<mgmt_version>}}mn|
}}mn| }}ynSMC URL:               }}cn<smc_url>}}mn|
}}mn| }}ynSMC Version:           }}cn<smc_version>}}mn|
}}mn| }}ynLaptop Admin User:     }}cn<admin_user>}}mn|
}}mn| }}ynStudent Username:      }}cn<student_user>}}mn|
}}mn| }}ynSystem Serial Number:  }}cn<bios_serial_number>}}mn|
}}mn| }}ynDisk Serial Number:    }}cn<disk_serial_number>}}mn|
}}mn======================================================================}}xx
            """
            col_size = 44
            txt = txt.replace("<mgmt_version>", mgmt_version.ljust(col_size))
            txt = txt.replace("<smc_url>", smc_url.ljust(col_size))
            txt = txt.replace("<smc_version>", smc_version.ljust(col_size))
            txt = txt.replace("<admin_user>", laptop_admin_user.ljust(col_size))
            txt = txt.replace("<admin_pass>", "******".ljust(col_size))
            student_text = student_user + " (" + student_full_name + ")"
            txt = txt.replace("<student_user>", student_text.ljust(col_size))
            txt = txt.replace("<bios_serial_number>", 
                CredentialProcess.COMPUTER_INFO['bios_serial_number'].ljust(col_size))
            txt = txt.replace("<disk_serial_number>", 
                CredentialProcess.COMPUTER_INFO['disk_boot_drive_serial_number'].ljust(col_size))

            p(txt)
            p("}}ybPress Y to continue: }}xx", False)
            tmp = input()
            tmp = tmp.strip().lower()
            if tmp != "y":
                p("}}cnCanceled - trying again....}}xx")
                continue

            # Show the warning regarding locking down the boot options
            p("""
}}mn======================================================================
}}mn| }}rb====================       WARNING!!!         ==================== }}mn|
}}mn| }}xxEnsure that the boot from USB or boot from SD card options in      }}mn|
}}mn| }}xxthe bios are disabled and that the admin password is set to a      }}mn|
}}mn| }}xxstrong random password.                                            }}mn|
}}mn======================================================================}}xx
            """)
            p("}}ybHave you locked down the BIOS? Press Y to continue: }}xx", False)
            tmp = input()
            tmp = tmp.strip().lower()
            if tmp != "y":
                p("}}cnCanceled - trying again....}}xx")
                continue

            # - Bounce off SMC - lms/credential_student.json/??
            result = None
            try:
                ex_info = dict()
                ex_info["logged_in_user"] = UserAccounts.get_current_user()
                ex_info["admin_user"] = laptop_admin_user
                ex_info["current_student"] = student_user
                ex_info["mgmt_version"] = mgmt_version
                
                ex_info.update(CredentialProcess.COMPUTER_INFO)

                result = RestClient.credential_student_in_smc(
                    student_user, smc_url, smc_admin_user, smc_admin_password,
                    dict(ex_info=ex_info))
                if result is None:
                    p("}}rbUnable to credential student via SMC!}}xx")
                    # Jump to top of loop and try again
                    continue
                    #return False # sys.exit(-1)
            except Exception as ex:
                p("}}rbError - Unable to credential student via SMC}}xx\n" + str(ex))
                # Jump to top of loop and try again
                continue
            
            (student_full_name, canvas_url, canvas_access_token,
            student_password, laptop_admin_password) = result
            loop_running = False

        ret = (student_user, student_full_name, student_password, laptop_admin_user,
            laptop_admin_password, canvas_access_token, canvas_url, smc_url)

        return ret

    @staticmethod
    def credential_laptop():
        
        # Are we running as admin w UAC??
        if not UserAccounts.is_uac_admin():
            p("}}rbNot Admin in UAC mode! - UAC Is required for credential process.}}xx")
            return False
        
        # Get computer info
        CredentialProcess.COMPUTER_INFO = Computer.get_machine_info(print_info=False)

        # Are we in a domain?
        if CredentialProcess.COMPUTER_INFO["cs_part_of_domain"] is True:
            p("}}rbSystem is doing to an Active Directory Domain - NOT SUPPORTED!\n" +
                "Please remove this from the domain as it might interfere with security settings.}}xx")
            return False
        
        # Are we using a proper edition win 10? (Home not supported, ed, pro, enterprise ok?)
        # OK - win 10 - pro, ed, enterprise
        # NOT OK - non win 10, win 10 home
        is_win10 = False
        is_win10_home = True
        os_caption = CredentialProcess.COMPUTER_INFO["os_caption"]
        if "Microsoft Windows 10" in os_caption:
            is_win10 = True
        if "Enterprise" in os_caption or "Professional" in os_caption or "Education" in os_caption:
            is_win10_home = False
        
        if is_win10 is not True:
            p("}}rbNOT RUNNING ON WINDOWS 10!!!\nThis software is designed to work win windows 10 ONLY!\n (Enterprise, Professional, or Education OK, Home edition NOT supported)}}xx")
            return False
        if is_win10_home is True:
            p("}}rbWIN10 HOME EDITION DETECTED!\nThis software is designed to work win windows 10 ONLY!\n (Enterprise, Professional, or Education OK, Home edition NOT supported)}}xx")
            return False

        # Disable guest account
        p("}}gnDisabling guest account}}xx", debug_level=2)
        UserAccounts.disable_guest_account()

        # Make sure folder exist and have proper permissions
        if not FolderPermissions.set_default_ope_folder_permissions():
            p("}}rbERROR - Unable to ensure folders are present and permissions are setup properly!}}xx")
            return False

        CredentialProcess.trust_ope_certs()

        # Disable all student accounts
        UserAccounts.disable_student_accounts()

        result = CredentialProcess.credential_input_verify_loop()
        if result is None:
            # Unable to verify?
            return False
        (student_user, student_name, student_password, admin_user, admin_password,
        canvas_access_token, canvas_url, smc_url) = result
        
        # - Create local student account
        p("}}gnCreating local student windows account...}}xx")
        if not UserAccounts.create_local_student_account(student_user, student_name, student_password):
            p("}}rbError setting up OPE Student Account}}xx\n " + str(ex))
            return False

        # - Setup admin user
        p("}}gnCreating local admin windows account...}}xx")
        try:
            UserAccounts.create_local_admin_account(admin_user, "OPE Laptop Admin", admin_password)
        except Exception as ex:
            p("}}rbError setting up OPE Laptop Admin Account}}xx\n " + str(ex))
        admin_password = ""

        # Store the credential information
        if not RegistrySettings.store_credential_info(canvas_access_token, canvas_url, smc_url,
            student_user, student_name, admin_user):
            p("}}rbError saving registry info!}}xx")
            return False
        
        # Create desktop shortcut
        #p("\n}}gnSetting up LMS App...}}xx")
        Computer.create_win_shortcut(
            lnk_path = "c:\\users\\public\\desktop\\OPE LMS.lnk",
            ico_path = "%programdata%\\ope\\Services\\lms\\logo_icon.ico",
            target_path = "%programdata%\\ope\\Services\\lms\\ope_lms.exe",
            description = "Offline LMS app for Open Prison Education project"
        )

        p("}}gnLocking machine - applying security settings...}}xx")
        if not CredentialProcess.lock_machine():
            p("}}rbERROR - Unable to lock machine after credentail!}}xx")
            return False
        
        return True

    @staticmethod
    def trust_ope_certs():
        # Download the CA crt and trust it so we don't get warnings/errors when visiting
        # the sites
        p("}}gnGetting OPE Cert file...}}xx", log_level=3)
        # Get the smc_url - pull the ca.crt file from there
        smc_url = RegistrySettings.get_reg_value(value_name="smc_url", default="https://smc.ed")
        
        app_path = util.get_app_folder()
        rc_path = os.path.join(app_path, "rc")
        wget_path = os.path.join(rc_path, "wget.exe")
        certmgr_path = os.path.join(rc_path, "certmgr.exe")
        tmp_path = os.path.expandvars("%programdata%\\ope\\tmp")
        crt_file = os.path.join(tmp_path, "ca.crt")
        
        crt_url = smc_url + "/static/certs/ca.crt"

        cmd = "\"" + wget_path + "\" --connect-timeout=6 --tries=3 --no-check-certificate -O \"" + crt_file + "\" " + crt_url

        returncode, output = ProcessManagement.run_cmd(cmd, cwd=tmp_path,
            require_return_code=0)
        if returncode == -2:
            # Error running command?
            p("}}rbError - unable to pull ca.crt file!}}xx\n" + output)
            return False
        p("Ret: " + str(returncode) + " - " + output, log_level=5)
        
        # Try to trust the cert
        cmd = "\"" + certmgr_path + "\" -add \"" + crt_file + "\" -c -s -r localMachine root "
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=tmp_path,
            require_return_code=0)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to add ca.crt file into trusted list!}}xx\n" + output)
            return False
        p("Ret: " + str(returncode) + " - " + output, log_level=5)
        
        return True
    
    @staticmethod
    def unlock_machine():
        # Remove security settings from the machine so it can be used by admins to do
        # maintenance/etc...
        ret = True

        # Make sure we disable student accounts!
        if not UserAccounts.disable_student_accounts():
            p("}}rbUnable to disable student accounts!}}xx")
            return False

        # Log out student accounts!
        if not UserAccounts.log_out_all_students():
            p("}}rbUnable to log out students!}}xx")
            return False
        
        # Reset group policy
        GroupPolicy.reset_group_policy_to_default()

        # Reset firewall
        GroupPolicy.reset_firewall_policy()


        return ret

    @staticmethod
    def ensure_opeservice_running():
        ret = False

        w = Computer.get_wmi_connection()

        services = w.Win32_Service(Name="OPEService")
        found = False
        for service in services:
            found = True
            if service.state == "Running":
                ret = True
            else:
                p("}}rbOPEService not in running state! " + str(service.state) + \
                    "\nTry rebooting and check again}}xx")

        if not found:
            p("}}rbOPEService not installed! - Try running credential again!}}xx")                
        return ret

    @staticmethod
    def lock_machine():
        # Apply secuirty settings and re-enable student account so it can be 
        # handed back to a student
        ret = True

        # Get the current credentialed student
        student_user_name = CredentialProcess.get_credentialed_student()
        if student_user_name is None:
            p("}}rbNot Credentiled! - Unable to find credentialed student - not locking machine!}}xx")
            return False
        
        # Get the current admin user name
        admin_user_name = CredentialProcess.get_credentialed_admin()
        if admin_user_name is None:
            p("}}rbNot Credentiled! - Unable to find credentialed admin account - not locking machine!}}xx")
            return False

        # Log out the student
        if not UserAccounts.log_out_user(student_user_name):
            p("}}rbError - Unable to logout student: " + str(student_user_name) + "}}xx")
            return False

        # Apply firewall rules
        if not GroupPolicy.apply_firewall_policy():
            p("}}rbError - Could Not apply firewall policy!\nStudent Account NOT unlocked!}}xx")
            return False

        # Apply group policy
        if not GroupPolicy.apply_group_policy():
            p("}}rbError - Could Not apply group policy!\nStudent Account NOT unlocked!}}xx")
            return False
        
        # Lock down boot options
        if not FolderPermissions.lock_boot_settings():
            p("}}rbError - Could not lock boot settings!\nStudent Account NOT unlocked!}}xx")
            return False

        # Reset registry permissions
        if not RegistrySettings.set_default_ope_registry_permissions():
            p("}}rbError - Could not reset registry permissions!\nStudent Account NOT unlocked!}}xx")
            return False

        # Reset folder permissions
        if not FolderPermissions.set_default_ope_folder_permissions():
            p("}}rbError - Could not reset ope folder permissions!\nStudent Account NOT unlocked!}}xx")
            return False
        
        # Reset student users group memberships
        if not UserAccounts.set_default_groups_for_student(student_user_name):
            p("}}rbError - Could not reset default groups for student!\nStudent Account NOT unlocked!}}xx")
            return False
        
        # Reset admin users group memberships
        if not UserAccounts.set_default_groups_for_admin(admin_user_name):
            p("}}rbError - Could not reset default groups for the admin account!\nStudent Account NOT unlocked!}}xx")
            return False
        
        # Ensure the OPEService is running
        if not CredentialProcess.ensure_opeservice_running():
            p("}}rbError - Verify OPEService is running!\nStudent Account NOT unlocked!}}xx")
            return False

        # Enable student account
        if not UserAccounts.enable_account(student_user_name):
            p("}}rbError - Failed to enable student account: " + str(student_user_name) + "}}xx")
            return False

        return ret


    @staticmethod
    def is_time_to_upgrade():
        # How long has it been since we tried to upgrade?
        last_upgrade_time = RegistrySettings.get_reg_value(value_name="last_upgrade_time", default=0)
        curr_time = time.time()

        # Only check for upgrades every 5 minutes
        if curr_time - last_upgrade_time > 300:
            return True
        
        return False

    @staticmethod
    def is_version_newer(current_version, remote_version):
        # Parse the strings and see which version is newer
        ret = False

        # Split out the parts
        cv_parts = current_version.split(".")
        rv_parts = remote_version.split(".")

        cv_major = 0
        cv_minor = 0
        cv_revision = 0

        try:
            cv_major = int(cv_parts[0])
        except:
            pass
        try:
            cv_minor = int(cv_parts[1])
        except:
            pass
        try:
            cv_revision = int(cv_parts[2])
        except:
            pass

        rv_major = 0
        rv_minor = 0
        rv_revision = 0

        try:
            rv_major = int(rv_parts[0])
        except:
            pass
        try:
            rv_minor = int(rv_parts[1])
        except:
            pass
        try:
            rv_revision = int(rv_parts[2])
        except:
            pass

        p(str(cv_major) + "." + str(cv_minor) + "." + str(cv_revision) + " -> " + \
            str(rv_major) + "." + str(rv_minor) + "." + str(rv_revision))
        # Is major version bigger?
        if rv_major > cv_major:
            ret = True
        # Is minor version bigger?
        if rv_major == cv_major and rv_minor > cv_minor:
            ret = True
        # Is revision bigger?
        if rv_major == cv_major and rv_minor == cv_minor and rv_revision > cv_revision:
            ret = True

        return ret

    @staticmethod
    def start_upgrade_process(branch=None, force_upgrade=None):
        ret = True

        if not CredentialProcess.is_time_to_upgrade():
            p("}}gnNot time to check for upgrades yet, skipping...}}xx", log_level=3)
            return True

        RegistrySettings.set_reg_value(value_name="last_upgrade_time", value=time.time())

        curr_branch = branch
        if curr_branch is None:
            # See if a parameter was provided
            curr_branch = util.get_param(2, None)
        
        # Force upgrade - even if versions match
        if force_upgrade is None:
            force_upgrade = util.get_param(3, "")
            if force_upgrade.lower() != "-f":
                force_upgrade = False
            else:
                force_upgrade = True
        
        # If branch is still empty, get it from the registry
        if curr_branch is None:
            curr_branch = RegistrySettings.get_reg_value(value_name="install_branch", default="master")

        # Start by grabbing any new stuff from the git server
        ret = ProcessManagement.git_pull_branch(curr_branch)
        if ret is False:
            # Not critical if this fails - apply whatever is present if it is
            # a different version number
            # return False
            p("}}ybWARNING - Unable to pull updates for git server!}}xx")
            pass
        
        # Save the current branch for next time
        RegistrySettings.set_reg_value(value_name="install_branch", value=curr_branch)

        # Check the mgmt.version files to see if we have a new version
        ope_laptop_binaries_path = os.path.expandvars("%programdata%\\ope\\tmp\\ope_laptop_binaries")
        # Get the path to the mgmt.version file
        git_version_path = os.path.join(ope_laptop_binaries_path, "Services", "mgmt", "mgmt.version")

        # Do we have a new version?
        curr_version = CredentialProcess.get_mgmt_version()
        git_version = CredentialProcess.get_mgmt_version(git_version_path)

        if git_version == "NO VERSION":
            # No version file found
            p("}}ynNo version file found in git repo, skipping upgrade!}}xx")
            return False
        
        if not CredentialProcess.is_version_newer(curr_version, git_version) and force_upgrade is not True:
            # Same version - no upgrade needed
            p("}}gnOPE Software up to date: " + str(git_version) + " not newer than " + str(curr_version) + " - (not upgrading)}}xx")
            return True

        # Version is different, prep for update
        forced = ""
        if force_upgrade:
            forced = "}}yb(upgrade forced)}}gn"
        p("}}gnFound new version " + forced + " - starting upgrade process: " + \
            curr_version + " --> " + git_version + "}}xx")
        
        # Lock user accounts
        if not UserAccounts.disable_student_accounts():
            p("}}rbERROR - Unable to disable student accounts prior to upgrade!}}xx")
            return False

        # Make sure students are logged out
        if not UserAccounts.log_out_all_students():
            p("}}rbERROR - Unable to log out student accounts prior to upgrade!}}xx")
            return False
        
        
        p("}}ynLaunching OPE Software Update process...}}xx")
        
        # run the upgrade_ope.cmd from the TMP rc folder!!!
        bat_path = os.path.join(ope_laptop_binaries_path, "Services\\mgmt\\rc\\upgrade_ope.cmd")
        # Add the redirect so we end up with a log file
        if not ProcessManagement.run_detatched_cmd(bat_path + " >> %programdata%\\ope\\tmp\\log\\upgrade.log 2>&1"):
            p("}}rbERROR - Unable to start upgrade process!}}xx")
            return False
        # Make sure to exit this app??
        #sys.exit(0)

        return ret

    @staticmethod
    def finish_upgrade_process():
        # If everything was successful, then
        # - Re-apply security
        # - lock_machine also re-enables credentialed account if succesful
        if not CredentialProcess.lock_machine():
            p("}}rbERROR - Unable to lock machine after upgrade!}}xx")
            return False

        p("}}gbSUCCESS! - Machine locked and user account enabled.}}xx")
        return True

    @staticmethod
    def sync_student_password():
        # Bounce off SMC to sync student password (in case it has changed)

        # Are we credentialed?

        # Send of info

        # Set password


        return True

    @staticmethod
    def push_logs_to_smc():
        # Gather log files/screenshots and send them off to the SMC server

        p("}}ybComing Soon...}}xx")
        return True

    @staticmethod
    def sync_lms_app_data():
        # Make the LMS app sync in headless mode (auto sync)

        p("}}ybComing Soon...}}xx")
        return True
    
    @staticmethod
    def sync_work_folder():
        # Start sync process to sync the home/work folder for the user

        p("}}ybComing Soon...}}xx")
        return True

    @staticmethod
    def is_time_to_ping_smc():
        # How long has it been since we talked to the SMC server?
        last_smc_ping_time = RegistrySettings.get_reg_value(value_name="last_smc_ping_time", default=0)
        curr_time = time.time()

        # Only need a successful ping every ? minutes
        min_time = 30  # TODO - Turn ping time back up 300
        time_diff = curr_time - last_smc_ping_time
        if time_diff > min_time:
            return True
        
        p("}}ynNot time to ping yet - " + str(int(min_time - time_diff)) + " seconds left.}}xx", log_level=4)
        return False

    @staticmethod
    def ping_smc(smc_url=None):
        # See if we can bounce off the SMC server and get a response
        if smc_url is None:
            # Try and get from command line
            smc_url = util.get_param(2, None)
        if smc_url is None:
            # Nothing on command line? Get from registry
            smc_url = RegistrySettings.get_reg_value(value_name="smc_url", default="https://smc.ed")

        force = util.get_param(3, "")
        if force == "-f":
            force = True
        else:
            force = False

        if not force and not CredentialProcess.is_time_to_ping_smc():
            #p("}}gnNot time to ping smc, skipping...}}xx", log_level=4)
            return True
        
        RegistrySettings.set_reg_value(value_name="last_smc_ping_time", value=time.time())
        
        if not RestClient.ping_smc(smc_url):
            p("}}mnNot able to ping SMC " + smc_url + "}}xx", log_level=4)
            # Ok to return true - we just don't do more maintenance
            return True

        # We are connected, do maintenance

        # Check if time to sync time
        SystemTime.sync_time_w_ntp()

        # Check if time to sync stuff (lms app, folders, logs)...
        # TODO 

        # Check if time to auto upgrade
        CredentialProcess.start_upgrade_process()

        return True

    @staticmethod
    def run_tests():
        p("}}gnRunning Tests...}}xx")

        #UserAccounts.disable_guest_account()
        #UserAccounts.disable_student_accounts()

        p(CredentialProcess.get_mgmt_version())
        pass


if __name__ == "__main__":
    CredentialProcess.run_tests()
    
