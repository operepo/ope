# import pythoncom
# import win32serviceutil
# import win32service
# import win32event
# import servicemanager
# import socket
# import time
# import datetime
# import sys
# import os
# import logging
# import random
# # from win32com.shell import shell, shellcon
# import ntsecuritycon
# import win32security
# import win32gui
# import win32ui
# import win32con
# import win32gui_struct
# import win32ts
# import win32process
# import win32profile
# import ctypes
# import wmi
# import traceback

import win32trace
import win32api
import sys
import os
import traceback

import util

# Pull in logger first and set it up!
from mgmt_EventLog import EventLog
global LOGGER
LOGGER = EventLog(os.path.join(util.LOG_FOLDER, 'ope-mgmt.log'), service_name="OPEMgmt")

from color import p, set_log_level

from mgmt_UserAccounts import UserAccounts
from mgmt_FolderPermissions import FolderPermissions
from mgmt_ScreenShot import ScreenShot
from mgmt_RegistrySettings import RegistrySettings
from mgmt_NetworkDevices import NetworkDevices
from mgmt_CredentialProcess import CredentialProcess
from mgmt_SystemTime import SystemTime
from mgmt_GroupPolicy import GroupPolicy
from mgmt_ProcessManagement import ProcessManagement
from mgmt_Computer import Computer
from mgmt_COMPorts import COMPorts
from mgmt_LockScreen import LockScreen


# Get the logging level
value_name = "log_level"
value = RegistrySettings.get_reg_value(app="OPEService",
    value_name=value_name, default=3, value_type="REG_DWORD")
set_log_level(value)

# Pre-declare - fill out later
global valid_commands
valid_commands = dict()


def RunAsTraceCollector():
	import sys
	try:
		import win32api
		win32api.SetConsoleTitle("Python Trace Collector")
	except:
		pass # Oh well!
	win32trace.InitRead()
	p("Collecting Python Trace Output...", log_level=4)
	try:
		while 1:
			# a short timeout means ctrl+c works next time we wake...
			sys.stdout.write(win32trace.blockingread(500))
	except KeyboardInterrupt:
		p("}}ybCtrl+C - quitting...}}xx", log_level=3)

def ensure_admin():
    # Get the is in administrators, is uac, and username and return them

    return (UserAccounts.is_in_admin_group(), UserAccounts.is_uac_admin(), 
        UserAccounts.get_current_user())

def show_version():
    ver = CredentialProcess.get_mgmt_version()
    p("}}gbVersion: " + str(ver) + "}}xx")
    return True

def show_help():
    global LOGGER, valid_commands
    # Find the help key for this command
    cmd = util.get_param(1).lower()
    param1 = util.get_param(2).lower()

    if cmd == "" or param1 == "":
        # Missing required parameters!
        p("}}rnMissing Required Parameters! " + cmd + " - " + param1 + "}}xx", log_level=1)
        return False
    
    if not param1 in valid_commands:
        p("}}rnInvalid Command! " + param1 + "}}xx", log_level=1)
        commands = list(valid_commands.keys())
        p("}}yn Valid Commands: " + str(commands) + "}}xx")
        p("}}ybFor help - type mgmt.exe help (command)}}xx")
        return False
    
    cmd_parts = valid_commands[param1]
    if cmd_parts is None:
        p("}}rnInvalid Command - not configured! " + param1 + "}}xx", log_level=1)
        return False
    
    help_msg = cmd_parts["help"]
    if help_msg is None:
        p("}}rnNo Help Provided! " + param1 + "}}xx", log_level=1)
        return False
    
    p("}}yb" + help_msg + "}}xx")
    return True


valid_commands = {  

    "help": {
        "function": show_help,
        "help": "Display help information for the specified command (e.g. mgmt.exe help set_log_level)",
    },

    ### SETTINGS ###
    # Add self to system path
    "add_mgmt_to_system_path": {
        "function": RegistrySettings.add_mgmt_utility_to_path,
        "help": "Add the path to the mgmt.exe file to the system path for easier use"
    },
    # Set log level
    "set_log_level": {
        "function": RegistrySettings.set_log_level,
        "help": "Adjust how verbose we want logging to be (default 3)"
    },
    # Set registry/folder run timer
    "set_default_permissions_timer": {
        "function": RegistrySettings.set_default_permissions_timer,
        "help": "How often do you want permissions reset on folder/registry (default 3600)"
    },
    # Set Frequency for scanning nics
    "set_scan_nics_timer": {
        "function": RegistrySettings.set_scan_nics_timer,
        "help": "How often do you want to scan nics for approved/disapproved nics (default 60)"
    },
    # How often should service reload settings
    "set_reload_settings_timer": {
        "function": RegistrySettings.set_reload_settings_timer,
        "help": "How often should the service reload settings from the registry (default 30)"
    },
    # Set how often to snap a screenshot
    "set_screen_shot_timer": {
        "function": RegistrySettings.set_screen_shot_timer,
        "help": "How often should we snap screen shots (default 30-300)"
    },

    # Show service trace log
    "show_trace": {
        "function": RunAsTraceCollector,
        "help": "Show console logs for the OPEService"
    }, 

    # Disable hostednetwork options on the wlan devices
    "disable_wlan_hosted_network": {
        "function": NetworkDevices.disable_wlan_hosted_network,
        "help": "Turn off hosted network options (nework sharing with other devices)"
    },
    "enable_wlan_hosted_network": {
        "function": NetworkDevices.enable_wlan_hosted_network,
        "help": "Turn on hosted network options (nework sharing with other devices)"
    },

    # Add/remove a nic from the approved list
    "approve_nic": {
        "function": NetworkDevices.approve_nic,
        "help": "Add a nic to the approved list - params include nic name (OR ID) and network subnet it is approved on\n" +
            "NOTE: Subnet should be first part of address - it is a simple match (e.g. 202.5.222 for 202.5.222.34)\n" +
            "mgmt.exe add_nic \"Intel(R) 82579LM Gigabit Network Connection\" 202.5.222",
    },
    "remove_nic": {
        "function": NetworkDevices.remove_nic,
        "help": "Remove a nic from the approved list - need both nic name and network\n" + 
            "mgmt.exe remove_nic \"Intel(R) 82579LM Gigabit Network Connection\" 202.5.222",
    },
    "list_approved_nics": {
        "function": NetworkDevices.list_approved_nics,
        "help": "Show a list of currently approved nics",
    },
    "list_system_nics": {
        "function": NetworkDevices.list_system_nics,
        "help": "Show a list of nics plugged into the system and their hardware status"
    },
    "get_machine_info": {
        "function": Computer.get_machine_info,
        "help": "Return some system information such as serial number"
    },
    


    ### SECURITY COMMANDS ###
    # Snap a screen shot of the users desktop
    "screen_shot": { 
        "function": ScreenShot.take_screenshot,
        "help": "Take a screen shot of the currently logged in user",
    },
    # Lock down permissions to OPE folders
    "set_default_ope_folder_permissions": {
        "function": FolderPermissions.set_default_ope_folder_permissions,
        "help": "Reset permissions on %programdata%\\ope folders",
    },
    # Lock down permissions to OPE registry entries
    "set_default_ope_registry_permissions": {
        "function": RegistrySettings.set_default_ope_registry_permissions,
        "help": "Reset permissions on OPE registry keys",
    },
    # Fire when a device status changes (nic plugged in?)
    "device_event": {
        "function": NetworkDevices.device_event,
        "help": "A device changed (plugged in?) - do the appropriate steps to keep system secure (fired as event from OPEService)"
    },
    # If any nics aren't in the approved list, disable them
    "scan_nics": {
        "function": NetworkDevices.scan_nics,
        "help": "Scan for nics that aren't approved and turn them off or on"
    },
    # Disable com ports not on the approved list (none?)
    "scan_com_ports": {
        "function": COMPorts.scan_com_ports,
        "help": "Find and disable com ports that we don't want enabled"
    },
    # Call to kill stuff if a credential fails mid-way (e.g. disable student users, lock things out)
    "bad_credential": {
        "function": UserAccounts.disable_student_accounts,
        "help": "If anything bad happens, make sure all student accounts are " + \
            "disabled so they can't use the system if it is returned to them by mistake"
    }, 

    # Apply group policy
    "apply_group_policy": {
        "function": GroupPolicy.apply_group_policy,
        "help": "Apply lock down windows group policy settings"
    },
    # Reset to win default group policy
    "reset_group_policy": {
        "function": GroupPolicy.reset_group_policy_to_default,
        "help": "Reset group policy to windows default (remove security)"
    },
    # Export the current group policy to a folder
    "export_group_policy": {
        "function": GroupPolicy.export_group_policy,
        "help": "Export the current group policy to a folder (e.g. mgmt export_group_policy exported_gpo )"
    },

    # Apply firewall Policy
    "apply_firewall_policy": {
        "function": GroupPolicy.apply_firewall_policy,
        "help": "Lock down firewall with pre-defined policy"
    },    
    # Reset firewall policy to default
    "reset_firewall_policy": {
        "function": GroupPolicy.reset_firewall_policy,
        "help": "Reset firewall policy back to factory defaults"
    },

    # Student Account Functions
    "create_student_account": {
        "function": UserAccounts.create_local_student_account,
        "help": "Create the student account in the windows system"
    },
    "remove_account": {
        "function": UserAccounts.delete_user,
        "help": "Remove the windows account AND profile from the system (e.g. mgmt remove_account s777777)"
    },
    "disable_account": {
        "function": UserAccounts.disable_account,
        "help": "Disable the specified windows account (e.g. mgmt disable_account s777777)"
    },
    "enable_account": {
        "function": UserAccounts.enable_account,
        "help": "Enable the specified windows account (e.g. mgmt enabl_account s777777)"
    },
    "disable_student_accounts": {
        "function": UserAccounts.disable_student_accounts,
        "help": "Disable ALL student accounts on this machine."
    },
    # Remove student profile folder (delete files)
    "remove_account_profile": {
        "function": UserAccounts.remove_account_profile,
        "help": "Remove the windows profile for this account (e.g. mgmt remove_account_profile s777777)"
    },
    # Download the OPE CA cert and add to the trusted list
    "trust_ope_certs": {
        "function": CredentialProcess.trust_ope_certs,
        "help": "Download CA crt from the OPE server and add to the trusted list"
    },
    # Lock the screen for the current user
    "lock_screen": {
        "function": UserAccounts.lock_screen_for_user,
        "help": "Lock the screen. If no user specified, locks the current screen.",
        "require_admin": False
    },
    "log_out_user": {
        "function": UserAccounts.log_out_user,
        "help": "Log out the specified user"
    },

    "lock_boot_settings": {
        "function": FolderPermissions.lock_boot_settings,
        "help": "Lock down boot settings so that you can't use safe mode or restore features"
    },
    "unlock_boot_settings": {
        "function": FolderPermissions.unlock_boot_settings,
        "help": "UnLock boot settings so that you can use restore features"
    },
    "update_uefi_boot_order": {
        "function": FolderPermissions.update_uefi_boot_order,
        "help": "Update boot order for UEFI boot settings"
    },

    "unlock_machine": {
        "function": CredentialProcess.unlock_machine,
        "help": "Disable student accounts and turn off security/policy/firewall settings - allow admins to plug in USB drive/etc..."
    },
    "lock_machine": {
        "function": CredentialProcess.lock_machine,
        "help": "Turn security features back on and re-enable student account."
    },
    "show_lock_screen_widget": {
        "function": LockScreen.show_lock_screen_widget,
        "help": "Launch the lock screen widget which shoes current state of syncing/updates/etc..."
    },
    "refresh_lock_screen_widget": {
        "function": LockScreen.refresh_lock_screen_widget,
        "help": "Update the lockscreen widget with the latest files and re-launch"
    },


    #### Do credential process ###
    "credential_laptop": {
        "function": CredentialProcess.credential_laptop,
        "help": "Run the credential process to lock down this laptop"
    },

    ### UPDATE/SYNC COMMANDS ###
    # Force a git pull
    "get_git_branch": {
        "function": RegistrySettings.get_git_branch,
        "help": "Get which branch to use when pulling updates from git repo"
    },
    "set_git_branch": {
        "function": RegistrySettings.set_git_branch,
        "help": "Set which branch to use when pulling updates from git repo"
    },
    "git_pull": {
        "function": ProcessManagement.git_pull_branch,
        "help": "Pull updates down from online or local SMC server"
    },

    # Upgrade everything from the smc server and restart services (if online)
    "start_upgrade": {
        "function": CredentialProcess.start_upgrade_process,
        "help": "Start the OPE software update process - processes will be stopped/started automatically\nCan also use position arguments to specify git branch and force update (e.g. mgmt.exe start_upgrade master -f)"
    },
    "finish_upgrade": {
        "function": CredentialProcess.finish_upgrade_process,
        "help": "Do follow-up steps after an upgrade (e.g. re-apply security, re-enable student account)"
    },

    # Bounce of SMC and get the current password for this student and set it 
    # in the local machine
    "sync_student_password": {
        "function": CredentialProcess.sync_student_password,
        "help": "Update the local login password from the server"
    },

    # Send screenshots/logs/reports to SMC (if online)
    "sync_logs_to_smc": {
        "function": CredentialProcess.sync_logs_to_smc,
        "help": "Push log files and screen shots to SMC server",
        "require_admin": False
    },
    # Sync users LMSApp Data w Canvas
    "sync_lms_app_data": {
        "function": CredentialProcess.sync_lms_app_data,
        "help": "Sync LMS App data in headless mode for the current student (auto sync)",
        "require_admin": False

    },
    # Sync users work folder with SMC
    "sync_work_folder": {
        "function": CredentialProcess.sync_work_folder,
        "help": "Sync work folders for the student (e.g. sync work files to desktop)",
        "require_admin": False
    },

    "sync_time": {
        "function": SystemTime.sync_time_w_ntp,
        "help": "Force time sync with the SMC server"
    },
    "ping_smc": {
        "function": CredentialProcess.ping_smc,
        "help": "Connect to the SMC server to see if we have connection"
    },

    "version": {
        "function": show_version,
        "help": "Display the version for the LMS software",
        "require_admin": False
    },

    "test_cmd": {
        "function": util.test_params,
        "help": "Debugging command",
        "hide": True,
    },

}


if __name__ == "__main__":
    # returns (is in admins, is uac, curr_user_name)
    is_admin = ensure_admin()

    # Parse Arguments
    cmd = util.get_param(1).lower()
    
    if cmd not in valid_commands:
        # Unknown Command??
        p("}}rnInvalid Command! - " + str(cmd) + "}}xx", log_level=1)

        # Only show commands if UAC active
        if is_admin[1]:
            # Remove hidden commands
            print_cmds = {}
            for k in valid_commands.keys():
                item = valid_commands[k]
                if not 'hide' in item or not item['hide'] is True:
                    print_cmds[k]=item

            commands = sorted(print_cmds.keys())
            p("}}yn Valid Commands: " + str(commands) + "}}xx")
            p("}}ybFor help - type mgmt.exe help (command)}}xx")
        sys.exit(1)
    
    # Run the function associated w the command
    cmd_parts = valid_commands[cmd]
    if cmd_parts is None:
        p("}}rnERROR - Command not avaialable " + cmd + " - coming soon...}}xx", log_level=1)
        sys.exit(1)
    
    cmd_requires_admin = util.get_dict_value(cmd_parts, "require_admin", True)

    if cmd_requires_admin is True and is_admin[1] is not True:
        # Command requires elevation and this user doesn't have it!

        if is_admin[0] is not True:
            # User is NOT in the administrators group
            p("}}rbINVALID USER - Must be in the administrators group to use this utility!\n" + 
                "Attempt logged for user " + is_admin[2] + ".}}xx", log_level=1)
            sys.exit(2)
            
        if is_admin[1] is not True:
            # User is NOT running with UAC enabled
            p("}}rbINVALID USER - Must be in UAC prompt to use this utility!\n" + 
                "Attempt logged for user " + is_admin[2] + ".}}xx", log_level=1)
            sys.exit(2)
        sys.exit(2)
    
    # Get the function assigned to this command
    f = cmd_parts["function"]
    if f is None:
        p("}}rnERROR - No function assigned to command " + cmd + " - coming soon...}}xx", log_level=1)
        sys.exit(1)

    exit_code = 0
    try:
        util.CMD_FUNCTION = cmd
        p("}}gnRunning " + cmd + "}}xx", log_level=4)
        ret = f()
        #p("}}ynReturn Code: " + str(ret) + "}}xx")
        if ret is not None and ret != True:
            exit_code = -1
    except Exception as ex:
        p("}}rnERROR: " + str(ex) + "}}xx", log_level=1)
        
        exit_code = 1
        
    # Clean exit
    sys.exit(exit_code)
    