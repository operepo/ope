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


import win32api
import sys
import os
import traceback

import util

from color import p

# Pull in logger first and set it up!
from mgmt_EventLog import EventLog
global LOGGER
LOGGER = EventLog(os.path.join(util.LOG_FOLDER, 'ope-mgmt.log'), service_name="OPE")

from mgmt_FolderPermissions import FolderPermissions
from mgmt_ScreenShot import ScreenShot
from mgmt_RegistrySettings import RegistrySettings
from mgmt_NetworkDevices import NetworkDevices


# Pre-declare - fill out later
global valid_commands
valid_commands = dict()

def ensure_admin():
    global LOGGER
    user_name = win32api.GetUserName()

    if not FolderPermissions.is_in_admin_group():
        # User isn't in the admin group!
        LOGGER.log_event("}}rbINVALID USER - Must be in the administrators group to use this utility!\n" + 
            "Attempt logged for user " + user_name + ".}}xx", log_level=1)

        sys.exit(1)
        return False
    if not FolderPermissions.is_admin():
         # User isn't an admin?
        LOGGER.log_event("}}rbINVALID USER - Must be in UAC prompt to use this utility!\n" + 
            "Attempt logged for user " + user_name + ".}}xx", log_level=1)

        sys.exit(1)
        return False
    
    return True

def show_help():
    global LOGGER, valid_commands
    # Find the help key for this command
    cmd = util.get_param(1).lower()
    param1 = util.get_param(2).lower()

    if cmd == "" or param1 == "":
        # Missing required parameters!
        LOGGER.log_event("}}rnMissing Required Parameters! " + cmd + " - " + param1 + "}}xx", log_level=1)
        return False
    
    if not param1 in valid_commands:
        LOGGER.log_event("}}rnInvalid Command! " + param1 + "}}xx", log_level=1)
        commands = list(valid_commands.keys())
        p("}}yn Valid Commands: " + str(commands) + "}}xx")
        p("}}ybFor help - type mgmt.exe help (command)}}xx")
        return False
    
    cmd_parts = valid_commands[param1]
    if cmd_parts is None:
        LOGGER.log_event("}}rnInvalid Command - not configured! " + param1 + "}}xx", log_level=1)
        return False
    
    help_msg = cmd_parts["help"]
    if help_msg is None:
        LOGGER.log_event("}}rnNo Help Provided! " + param1 + "}}xx", log_level=1)
        return False
    
    LOGGER.log_event("}}yb" + help_msg + "}}xx")
    return True


valid_commands = {  

    "help": {
        "function": show_help,
        "help": "",
    },

    ### SETTINGS ###
    # Add self to system path
    "add_mgmt_to_system_path": {
        "function": None,
        "help": "Add the path to the mgmt.exe file to the system path for easier use"
    },
    # Set log level
    "set_log_level": None,
    # Set registry/folder run frequency
    "set_default_permissions_frequency": None,
    # Set Frequency for scanning nics
    "set_scan_nics_frequency": None,
    # How often should service reload settings
    "set_reload_settings_frequency": None,
    # Set how often to snap a screenshot
    "set_screen_shot_frequency": None,

    # Add/remove a nic from the approved list
    "approve_nic": {
        "function": NetworkDevices.approve_nic,
        "help": "Add a nic to the approved list - params include nic name (OR ID) and netowrk subnet it is approved on\n" +
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
    


    ### SECURITY COMMANDS ###
    # Snap a screen shot of the users desktop
    "screen_shot": { 
        "function": ScreenShot.take_screenshot,
        "help": "Take a screen shot of the currently logged in user",
    },
    # Lock down permissions to OPE folders
    "set_default_ope_folder_permissions": {
        "function": FolderPermissions.set_default_ope_folder_permissions,
        "help": "Reset permissions on %programdata%\ope folders",
    },
    # Lock down permissions to OPE registry entries
    "set_default_ope_registry_permissions": {
        "function": RegistrySettings.set_default_ope_registry_permissions,
        "help": "Reset permissions on OPE registry keys",
    },
    # Fire when a device status changes (nic plugged in?)
    "device_event": None,
    # If any nics aren't in the approved list, disable them
    "scan_nics": {
        "function": NetworkDevices.scan_nics,
        "help": "Scan for nics that aren't approved and turn them off or on"
    },
    # Disable com ports not on the approved list (none?)
    "scan_com_ports": None, 
    # Call to kill stuff if a credential fails mid-way (e.g. disable student users, lock things out)
    "bad_credential": None, 

    # Apply group policy
    "apply_group_policy": None,
    # Reset to win default group policy
    "reset_group_policy": None,

    # Apply firewall Policy
    "apply_firewall_policy": None,
    # Reset firewall policy to default
    "reset_firewall_policy": None,

    # Student Account Functions
    "create_student_account": None,
    "remove_student_account": None,
    "disable_student_account": None,
    # Remove student profile folder (delete files)
    "remove_studnt_profile": None,

    ### UPDATE/SYNC COMMANDS ###
    # Upgrade everything from the smc server and restart services (if online)
    "upgrade_software": None,

    # Send screenshots/logs/reports to SMC (if online)
    "push_logs_to_smc": None,
    # Sync users LMSApp Data w Canvas
    "sync_lms_app_data": None,
    # Sync users work folder with SMC
    "sync_work_folder": None,

}


if __name__ == "__main__":
    if not ensure_admin():
        sys.exit(1)
    
    # Parse Arguments
    cmd = util.get_param(1).lower()
    
    if cmd not in valid_commands:
        # Unknown Command??
        LOGGER.log_event("}}rnInvalid Command! - " + str(cmd) + "}}xx", log_level=1)
        commands = list(valid_commands.keys())
        p("}}yn Valid Commands: " + str(commands) + "}}xx")
        p("}}ybFor help - type mgmt.exe help (command)}}xx")
        sys.exit(1)

    # Run the function associated w the command
    cmd_parts = valid_commands[cmd]
    if cmd_parts is None:
        LOGGER.log_event("}}rnERROR - Command not avaialable " + cmd + "}}xx", log_level=1)
        sys.exit(1)
    
    
    # Get the function assigned to this command
    f = cmd_parts["function"]
    if f is None:
        LOGGER.log_event("}}rnERROR - No function assigned to command " + cmd + "}}xx", log_level=1)
        sys.exit(1)
    
    try:
        LOGGER.log_event("}}gnRunning " + cmd + "}}xx")
        f()
    except Exception as ex:
        LOGGER.log_event("}}rnERROR: " + str(ex) + "}}xx", log_level=1)
        traceback.print_exc()
        
        sys.exit(1)
        
    # Clean exit
    sys.exit(0)
    