
# Needed for folder security
import win32security
import win32api
import ntsecuritycon
import win32net
import ctypes

import sys
import os
import traceback
import time
import logging

import util

from color import p

from mgmt_ProcessManagement import ProcessManagement
from mgmt_RegistrySettings import RegistrySettings


class FolderPermissions:
    # Class to deal with folder permissions
    
    GROUP_EVERYONE = None
    GROUP_ADMINISTRATORS = None
    CURRENT_USER = None
    SYSTEM_USER = None
    
    @staticmethod
    def init_win_user_accounts():
        # Load account information for groups/users
        domain = None
        acct_type = None
        
        if FolderPermissions.GROUP_EVERYONE is None:
            EVERYONE, domain, acct_type = win32security.LookupAccountName("", "Everyone")
            FolderPermissions.GROUP_EVERYONE = EVERYONE
            
        if FolderPermissions.GROUP_ADMINISTRATORS is None:
            ADMINISTRATORS, domain, acct_type = win32security.LookupAccountName("", "Administrators")
            FolderPermissions.GROUP_ADMINISTRATORS = ADMINISTRATORS
        
        if FolderPermissions.CURRENT_USER is None:
            CURRENT_USER, domain, acct_type = win32security.LookupAccountName("", win32api.GetUserName())
            
            if CURRENT_USER is None:
                try:
                    CURRENT_USER, domain, acct_type = win32security.LookupAccountName("", "huskers")
                except:
                    CURRENT_USER = None
                if CURRENT_USER is None:
                    try:
                        CURRENT_USER, domain, acct_type = win32security.LookupAccountName("", "ray")
                    except:
                        CURRENT_USER = None
            FolderPermissions.CURRENT_USER = CURRENT_USER
        
        if FolderPermissions.SYSTEM_USER is None:
            SYSTEM_USER, domain, acct_type = win32security.LookupAccountName("", "System")
            FolderPermissions.SYSTEM_USER = SYSTEM_USER

        # Pretend to use these so pylint shuts up
        if domain is None or acct_type is None:
            pass
        

    @staticmethod
    def show_cacls(filename):
        p("\n\n")    
        for line in os.popen("cacls %s" % filename).read().splitlines():
            p(line)
    
    @staticmethod
    def set_ope_folder_permissions(folder_path, everyone_rights="r", walk_files=True):
        # everyone_rights: r - readonly, n - none, rw - readwrite, f - full, c - create/append
        # a - append (for files?)
    
        # EVERYONE - Figure out proper perms for everyone group
        everyone_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
        if everyone_rights == "r":
            everyone_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
        if everyone_rights == "n":
            everyone_perms = 0
        if everyone_rights == "rw":
            everyone_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE | ntsecuritycon.FILE_GENERIC_WRITE
        if everyone_rights == "f":
            everyone_perms = ntsecuritycon.FILE_ALL_ACCESS
        if everyone_rights == "c":
            everyone_perms = ntsecuritycon.FILE_ADD_FILE | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
        if everyone_rights == "a":
            everyone_perms = ntsecuritycon.FILE_APPEND_DATA | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
    
        # Make sure our global accounts are available
        FolderPermissions.init_win_user_accounts()
        
        # All folders get admins/system_user/current_user (logged in admin) full rights
        # and limited rights for the everyone group
        
        # Setup new DACL for the folder
        # Set inheritance flags
        flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
        sd = win32security.GetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION)
        # Create the blank DACL and add our ACE's
        dacl = win32security.ACL()
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.GROUP_ADMINISTRATORS)
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.SYSTEM_USER)
        # Make sure current user (admin running this) has rights too
        if not FolderPermissions.CURRENT_USER is None:
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.CURRENT_USER)
        
        if everyone_perms != 0:
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags,
                                   everyone_perms,
                                   FolderPermissions.GROUP_EVERYONE)
        # Set our ACL
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        win32security.SetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)
        
        # Possible to set whole tree? - Doesn't seem to work, use file walk instead
        # win32security.TreeSetNamedSecurityInfo(folder, win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, None, None, sd, None)
        
        # Walk sub folders 
        if walk_files is True:
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for f in files:
                    try:
                        win32security.SetFileSecurity(os.path.join(root, f), win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)
                    except:
                        logging.info("Error setting file permissions " + os.path.join(root, f))
                for d in dirs:
                    try:
                        win32security.SetFileSecurity(os.path.join(root, d), win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)
                    except:
                        logging.info("Error setting folder permissions " + os.path.join(root, d))

            
        return
    
    @staticmethod
    def is_time_to_set_default_ope_folder_permissions():
        # How long has it been since we synced our time?
        last_time_sync = RegistrySettings.get_reg_value(value_name="last_apply_ope_folder_permissions", default=0)
        curr_time = time.time()

        set_default_permissions_timer = RegistrySettings.get_reg_value(value_name="apply_ope_folder_permissions_timer", default=3600*3)

        # Only sync every ?? minutes
        if curr_time - last_time_sync > set_default_permissions_timer:
            return True
        
        return False
    
    @staticmethod
    def set_default_ope_folder_permissions(force=False):

        # Command that is run to start this function
        only_for = "set_default_ope_folder_permissions"
        param_force = util.pop_force_flag(only_for=only_for)
        if force is False:
            force = param_force
        
        if force is not True and not FolderPermissions.is_time_to_set_default_ope_folder_permissions():
            p("}}gnNot time to set ope folder permissions yet, skipping.}}xx", log_level=4)
            return True

        # Set permissions on OPE folder so inmates can't change things
        p("}}gnTrying to set OPE Folder Permissions...}}xx", log_level=3)

        RegistrySettings.set_reg_value(value_name="last_apply_ope_folder_permissions", value=time.time(), value_type="REG_DWORD")
        
        # Load up the system goups/users
        FolderPermissions.init_win_user_accounts()
        
        # Make sure folders exits
        if not os.path.isdir(util.ROOT_FOLDER):
            os.makedirs(util.ROOT_FOLDER, exist_ok=True)
        if not os.path.isdir(util.TMP_FOLDER):
            os.makedirs(util.TMP_FOLDER, exist_ok=True)
        if not os.path.isdir(util.LOCK_SCREEN_WIDGET_FOLDER):
            os.makedirs(util.LOCK_SCREEN_WIDGET_FOLDER, exist_ok=True)
        if not os.path.isdir(util.LOG_FOLDER):
            os.makedirs(util.LOG_FOLDER, exist_ok=True)
        if not os.path.isdir(util.SCREEN_SHOTS_FOLDER):
            os.makedirs(util.SCREEN_SHOTS_FOLDER, exist_ok=True)
        if not os.path.isdir(util.BINARIES_FOLDER):
            os.makedirs(util.BINARIES_FOLDER, exist_ok=True)
        if not os.path.isdir(util.GIT_FOLDER):
            os.makedirs(util.GIT_FOLDER, exist_ok=True)
        if not os.path.isdir(util.STUDENT_DATA_FOLDER):
            os.makedirs(util.STUDENT_DATA_FOLDER, exist_ok=True)
        
        # ---- ope-sshot.log ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "ope-sshot.log")):
            f = open(os.path.join(util.LOG_FOLDER, "ope-sshot.log"), "w")
            f.close()
        
        # ---- ope-mgmt.log ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "ope-mgmt.log")):
            f = open(os.path.join(util.LOG_FOLDER, "ope-mgmt.log"), "w")
            f.close()
        
        # ---- ope-state.log ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "ope-state.log")):
            f = open(os.path.join(util.LOG_FOLDER, "ope-state.log"), "w")
            f.close()
        
        # ---- lms_app_debug.log ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "lms_app_debug.log")):
            f = open(os.path.join(util.LOG_FOLDER, "lms_app_debug.log"), "w")
            f.close()
        
        # ---- upgrade.log ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "upgrade.log")):
            f = open(os.path.join(util.LOG_FOLDER, "upgrade.log"), "w")
            f.close()
        
        # App folder permissions are set based on this list 
        # r - read/execute, n - none, c - create/append, a - appendonly, f - full
        app_folders = {
            util.ROOT_FOLDER: "r",
            util.BINARIES_FOLDER: "r",
            util.STUDENT_DATA_FOLDER: "r",
            util.TMP_FOLDER: "r",
            util.GIT_FOLDER: "r",  # TODO - change to n when we can avoid security prompts
            util.LOG_FOLDER: "c",
            os.path.join(util.LOG_FOLDER, "ope-sshot.log"): "a",
            os.path.join(util.LOG_FOLDER, "ope-mgmt.log"): "a",
            os.path.join(util.LOG_FOLDER, "ope-state.log"): "r",
            os.path.join(util.LOG_FOLDER, "lms_app_debug.log"): "a",
            os.path.join(util.LOG_FOLDER, "upgrade.log"): "r",
            util.SCREEN_SHOTS_FOLDER: "c",
            util.LOCK_SCREEN_WIDGET_FOLDER: "r",
            
        }
        
        for f in app_folders.keys():
            everyone_rights = app_folders[f]
            p("}}gnSetting permissions on " + f + " (rights for everyone " + \
                everyone_rights + ")}}xx", log_level=5)
            FolderPermissions.set_ope_folder_permissions(f, everyone_rights=everyone_rights)

        return True
    
    @staticmethod
    def lock_boot_settings():
        ret = True

        # Get the default from the boot manager
        cmd = "%SystemRoot%\\System32\\bcdedit.exe"
        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=3, require_return_code=0)
        #p(str(returncode) + " - " + output)
        if returncode == -2:
            # Error running command?
            p("}}rbError - get boot options!}}xx\n" + output)
            return False
        
        # Is the boot manager listed as {current} or {default}
        boot_identifier = "{current}"
        if "{default}" in output:
            boot_identifier = "{default}"
        
        p("}}gnBoot ID: " + boot_identifier + "}}xx", log_level=5)

        # https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/%SystemRoot%\\system32\\bcdedit.exe--set

        # Lock down boot settings
        # (cmd, required_return_code)
        cmds = [
            ("%SystemRoot%\\System32\\bcdedit.exe /timeout 0", 0),
            
            ("%SystemRoot%\\system32\\bcdedit.exe /set {bootmgr} displaybootmenu no", 0),
            # Use standard policy - no F8 key
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " bootmenupolicy Standard", 0),
            # Try to boot normally every time - helps to not show recovery options
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " bootstatuspolicy ignoreallfailures", 0),
            # Disable recovery
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " recoveryenabled off", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set {globalsettings} recoveryenabled off", 0),
            # Disable Advanced Options
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " advancedoptions off", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set {globalsettings} advancedoptions off", 0),

            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " bootems off", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " optionsedit off", 0),

            # disable Win Recovery Environment (WinRE)
            ("%SystemRoot%\\system32\\reagentc /disable", None),

            ("%SystemRoot%\\system32\\bcdedit.exe /deletevalue " + boot_identifier + " safeboot ", None),

        ]

        for tcmd in cmds:
            cmd = tcmd[0]
            require_return_code = tcmd[1]
            cmd = os.path.expandvars(cmd)
            returncode, output = ProcessManagement.run_cmd(cmd,
                attempts=3, require_return_code=require_return_code)
            p(str(returncode) + " - " + output, log_level=5)
            if returncode == -2:
                # Error running command?
                p("}}rbError - set boot options!}}xx\n" + output)
                return False


        # Ensure that RE is disabled
        # Get the default from the boot manager
        cmd = "%SystemRoot%\\system32\\reagentc /info"
        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=3, require_return_code=0)
        p(str(returncode) + " - " + output, log_level=5)
        if returncode == -2:
            # Error running command?
            p("}}rbError - get reagentc /info!}}xx\n" + output)
            return False
        
        if "Disabled" not in output:
            p("}}rbERROR - Windows Recovery Environment NOT disabled!}}xx")
            return False
        else:
            p("}}gnWinRE Disabled!}}xx", log_level=3)

        # ALT INFO - shouldn't need these w current commands
        # rem Option to kill safemode w bluescreen/error
        # rem HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\SafeBoot
        # rem rename "minimal" and "Network" to cause blue screens
        # rem OK IF THERE ARE FAILURES ON SECOND RUNS!
        # rem echo Modifying Registry to break safeboot
        # rem reg copy HKLM\System\CurrentControlSet\Control\SafeBoot\Minimal HKLM\System\CurrentControlSet\Control\SafeBoot\MinimalX /s /f
        # rem reg delete HKLM\System\CurrentControlSet\Control\SafeBoot\Minimal /f

        # rem reg copy HKLM\System\CurrentControlSet\Control\SafeBoot\Network HKLM\System\CurrentControlSet\Control\SafeBoot\NetworkX /s /f
        # rem reg delete HKLM\System\CurrentControlSet\Control\SafeBoot\Network /f

        # rem todo - return proper error
        # rem return 0 for now so we don't blow up credential process



        return ret

    
    @staticmethod
    def unlock_boot_settings():
        # Get the default from the boot manager
        cmd = "%SystemRoot%\\System32\\bcdedit.exe"
        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=3, require_return_code=0)
        #p(str(returncode) + " - " + output)
        if returncode == -2:
            # Error running command?
            p("}}rbError - get boot options!}}xx\n" + output)
            return False
        
        # Is the boot manager listed as {current} or {default}
        boot_identifier = "{current}"
        if "{default}" in output:
            boot_identifier = "{default}"

        p("}}gnBoot ID: " + boot_identifier + "}}xx", log_level=4)

        cmds = [
            ("%SystemRoot%\\System32\\bcdedit.exe /timeout 30", 0),
            
            ("%SystemRoot%\\system32\\bcdedit.exe /set {bootmgr} displaybootmenu yes", 0),
            # Use standard policy - no F8 key
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " bootmenupolicy Standard", 0),
            # Try to boot normally every time - helps to not show recovery options
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " bootstatuspolicy IgnoreShutdownFailures", 0),
            # Disable recovery
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " recoveryenabled on", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set {globalsettings} recoveryenabled on", 0),
            # Disable Advanced Options
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " advancedoptions on", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set {globalsettings} advancedoptions on", 0),

            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " bootems on", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set " + boot_identifier + " optionsedit on", 0),

            # enable Win Recovery Environment (WinRE)
            ("%SystemRoot%\\system32\\reagentc /enable", None),
            # issues enabling?
            # https://www.terabyteunlimited.com/kb/article.php?id=587
            # bcdboot c:\windows /v

            #"%SystemRoot%\\system32\\bcdedit.exe /deletevalue " + boot_identifier + " safeboot ",

        ]

        for tcmd in cmds:
            cmd = tcmd[0]
            require_return_code = tcmd[1]
            cmd = os.path.expandvars(cmd)
            returncode, output = ProcessManagement.run_cmd(cmd,
                attempts=3, require_return_code=require_return_code)
            p(str(returncode) + " - " + output)
            if returncode == -2:
                # Error running command?
                p("}}rbError - set boot options!}}xx\n" + output)
                return False
        
        return False
      

if __name__ == "__main__":
    p("Testing:")
    