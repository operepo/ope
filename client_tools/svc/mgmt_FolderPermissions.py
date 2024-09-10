
# Needed for folder security
import win32security
import win32api
import ntsecuritycon
import win32net
import ctypes
import uuid

from firmware_variables import *
from firmware_variables.load_option  import LoadOptionAttributes, LoadOption
from firmware_variables.device_path import DevicePathList, DevicePath, DevicePathType, MediaDevicePathSubtype, EndOfHardwareDevicePathSubtype
from firmware_variables.utils import verify_uefi_firmware, string_to_utf16_bytes, utf16_string_from_bytes
import struct



import sys
import os
import traceback
import time
import logging

import util

from color import p

from mgmt_ProcessManagement import ProcessManagement
from mgmt_RegistrySettings import RegistrySettings
from mgmt_UserAccounts import UserAccounts

class FolderPermissions:
    # Class to deal with folder permissions
    
    GROUP_EVERYONE = None
    GROUP_ADMINISTRATORS = None
    CURRENT_USER = None
    SYSTEM_USER = None
    OPE_STUDENTS = None
    OPE_ADMINS = None
    
    @staticmethod
    def init_win_user_accounts():
        # Load account information for groups/users
        domain = None
        acct_type = None

        UserAccounts.create_local_admins_group()
        UserAccounts.create_local_students_group()

        if FolderPermissions.OPE_STUDENTS is None:
            OPE_STUDENTS, domain, acct_type = win32security.LookupAccountName("", "OPEStudents")
            FolderPermissions.OPE_STUDENTS = OPE_STUDENTS
        
        if FolderPermissions.OPE_ADMINS is None:
            OPE_ADMINS, domain, acct_type = win32security.LookupAccountName("", "OPEAdmins")
            FolderPermissions.OPE_ADMINS = OPE_ADMINS
        
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
    def set_ope_folder_permissions(folder_path, everyone_rights="r", walk_files=True, ope_students_rights="r", add_current_user=False):
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
    
        # Figure out OPE Students perms
        ope_students_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
        if ope_students_rights == "r":
            ope_students_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
        if ope_students_rights == "n":
            ope_students_perms = 0
        if ope_students_rights == "rw":
            ope_students_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE | ntsecuritycon.FILE_GENERIC_WRITE
        if ope_students_rights == "f":
            ope_students_perms = ntsecuritycon.FILE_ALL_ACCESS
        if ope_students_rights == "c":
            ope_students_perms = ntsecuritycon.FILE_ADD_FILE | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE
        if ope_students_rights == "a":
            ope_students_perms = ntsecuritycon.FILE_APPEND_DATA | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE


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
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.OPE_ADMINS)

        # Make OPE_Students get the same rights as everyone
        if ope_students_perms != 0:
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ope_students_perms, FolderPermissions.OPE_STUDENTS)

        # Make sure current user (admin running this) has rights too
        if add_current_user is True and not FolderPermissions.CURRENT_USER is None:
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
    def get_acl_rights_for_user(folder_path, username):
        # Look at the ACL, see if this user is allowed to access this folder
        ret = []

        # Make sure our global accounts are available
        FolderPermissions.init_win_user_accounts()

        OWNER = d = atime = None
        try:
            OWNER, d, atype = win32security.LookupAccountName("", username)
        except:
            p("is_user_in_acl - Unable to find user: " + str(username))
            return None        

        sd = win32security.GetFileSecurity(
            folder_path,
            win32security.DACL_SECURITY_INFORMATION |
            win32security.OWNER_SECURITY_INFORMATION |
            win32security.GROUP_SECURITY_INFORMATION |
            win32security.SACL_SECURITY_INFORMATION
            )
        o, d, atime = win32security.LookupAccountSid(None, sd.GetSecurityDescriptorOwner())
        if o == username:
            ret.append("o")
        
        dacl = sd.GetSecurityDescriptorDacl()
        mask = dacl.GetEffectiveRightsFromAcl(
            {
                'TrusteeForm': win32security.TRUSTEE_IS_NAME,
                'TrusteeType': win32security.TRUSTEE_IS_USER,
                'Identifier': username
            }
        )

        if bool(mask & 0x00000001):
            ret.append('r') # read
        if bool(mask & 0x00000002):
            ret.append('w') # write
        if bool(mask & 0x00000004):
            ret.append('a') # append
        if bool(mask & 0x00000008):
            ret.append('rea') # read ea
        if bool(mask & 0x00000010):
            ret.append('wea')  # write ea
        if bool(mask & 0x00000020):
            ret.append('x')   # execute
        if bool(mask & 0x00000040):
            ret.append('dc') # delete children
        if bool(mask & 0x00000080):
            ret.append("ra")  # read attributes
        if bool(mask & 0x00000100):
            ret.append("wa")  # write attributes
        if bool(mask & 0x00010000):
            ret.append('d')  # delete
        if bool(mask & 0x00020000):
            ret.append('rc')  # Read Control
        if bool(mask & 0x00040000):
            ret.append('wdac')  # write dac
        if bool(mask & 0x00080000):
            ret.append('wo')    # write owner
        if bool(mask & 0x00100000):
            ret.append('s') # syncronise
        
        return ret

    @staticmethod
    def set_home_folder_permissions(folder_path, owner_user, walk_files=True):
        if owner_user is None or owner_user == "":
            p("Invalid Owner, can't set home folder permissions: " + str(folder_path))
            return False

        # owner_rights: r - readonly, n - none, rw - readwrite, f - full, c - create/append
        # a - append (for files?)

        #owner_perms = ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE | ntsecuritycon.FILE_GENERIC_WRITE
        owner_perms = ntsecuritycon.FILE_ALL_ACCESS
    
        # Make sure our global accounts are available
        FolderPermissions.init_win_user_accounts()

        OWNER = d = atime = None
        try:
            OWNER, d, atype = win32security.LookupAccountName("", owner_user)
        except:
            p("Unable to find user: " + str(owner_user))
            return False
                
        # Setup new DACL for the folder
        # Set inheritance flags
        flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
        sd = win32security.GetFileSecurity(folder_path, win32security.DACL_SECURITY_INFORMATION)
        # Create the blank DACL and add our ACE's
        dacl = win32security.ACL()
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.GROUP_ADMINISTRATORS)
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.SYSTEM_USER)
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.OPE_ADMINS)

        # Make sure current user (admin running this) has rights too
        if not FolderPermissions.CURRENT_USER is None:
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, FolderPermissions.CURRENT_USER)
        
        if owner_perms != 0:
            dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags,
                                   owner_perms,
                                   OWNER)
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

            
        return True
    
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
        if not os.path.isdir(util.CONFIG_FOLDER):
            os.makedirs(util.CONFIG_FOLDER, exist_ok=True)
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
        
        # ---- ope-config.json ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.CONFIG_FOLDER, "ope-config.json")):
            f = open(os.path.join(util.CONFIG_FOLDER, "ope-config.json"), "w")
            f.close()
        
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
        
         # ---- ope-lockscreen.log ----
        # Make sure the log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "ope-lockscreen.log")):
            f = open(os.path.join(util.LOG_FOLDER, "ope-lockscreen.log"), "w")
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
        # (everyone, ope_students, add_current_user)
        app_folders = {
            util.ROOT_FOLDER: ("r", "r", False),
            util.CONFIG_FOLDER: ("n", "r", False),
            util.BINARIES_FOLDER: ("r", "r", False),
            util.STUDENT_DATA_FOLDER: ("r", "r", False),
            util.TMP_FOLDER: ("r", "r", False),
            util.GIT_FOLDER: ("r", "r", False),  # TODO - change to n when we can avoid security prompts
            util.LOG_FOLDER: ("c", "c", False),
            os.path.join(util.CONFIG_FOLDER, "ope-config.json"): ("n", "n", False),
            os.path.join(util.LOG_FOLDER, "ope-sshot.log"): ("a", "a", False),
            os.path.join(util.LOG_FOLDER, "ope-mgmt.log"): ("a", "a", False),
            os.path.join(util.LOG_FOLDER, "ope-lockscreen.log"): ("a", "a", False),
            os.path.join(util.LOG_FOLDER, "ope-state.log"): ("r", "r", False),
            os.path.join(util.LOG_FOLDER, "lms_app_debug.log"): ("a", "a", False),
            os.path.join(util.LOG_FOLDER, "upgrade.log"): ("r", "r", False),
            util.SCREEN_SHOTS_FOLDER: ("c", "c", False),
            util.LOCK_SCREEN_WIDGET_FOLDER: ("r", "r", False),
            
        }
        
        for f in app_folders.keys():
            (everyone_rights, ope_student_rights, add_current_user) = app_folders[f]
            p("}}gnSetting permissions on " + f + " (rights for everyone " + \
                everyone_rights + ")(rights for ope students " + ope_student_rights + ")(add current user " + str(add_current_user) + ")}}xx", log_level=5)
            FolderPermissions.set_ope_folder_permissions(f, everyone_rights=everyone_rights, ope_students_rights=ope_student_rights, add_current_user=add_current_user)

        return True
    
    @staticmethod
    def rebuild_bcd_data_wmi():
        GUID_WINDOWS_BOOTMGR = "{9dea862c-5cdd-4e70-acc1-f32b344d4795}"
        GUID_WINDOWS_FWBOOTMGR = "{a5a30fa2-3d06-4e9f-b5f4-a01df9d1fcba}"
        GUID_DEBUGGER_SETTINGS_GROUP = "{4636856e-540f-4170-a130-a84776f4c654}"
        GUID_CURRENT_BOOT_ENTRY = "{fa926493-6f1c-4193-a414-58f0b2456d1e}"      # {current} or 
        GUID_DEFAULT_BOOT_ENTRY = ""                                            # {default}??
        GUID_WINDOWS_LEGACY_NTLDR = "{466f5a88-0af2-4f76-9038-095b170dc21c}"
        GUID_WINDOWS_MEMORY_DIAG = "{b2721d73-1db4-4c62-bf78-c548a880142d}"     # {memdiag}
        GUID_WINDOWS_RESUME = "{147aa509-0358-4473-b83b-d950dda00615}"
        
        
        GUID_WINDOWS_BADMEMORY = "{5189b25c-5558-4bf2-bca4-289b11bd29e2}"       # {badmemory}
        GUID_BOOT_LOADER_SETTINGS = "{6efb52bf-1766-41db-a6b3-0ee5eff72bd7}"    # {bootloadersettings}
        GUID_EMS_SETTINGS = "{0ce4991b-e6b3-4b16-b23c-5e0d9250e5d9}"            # {emssettings}
        GUID_GLOBAL_SETTINGS = "{7ea2e1ac-2e61-4728-aaa3-896d9d0a9f0e}"         # {globalsettings}
        GUID_RESUME_LOADER_SETTINGS = "{1afa9c49-16ab-4a5c-901b-212802da9460}"  # {resumeloadersettings}

        BCDE_DEVICE_TYPE_BOOT_DEVICE    =0x00000001
        BCDE_DEVICE_TYPE_PARTITION      =0x00000002
        BCDE_DEVICE_TYPE_FILE           =0x00000003
        BCDE_DEVICE_TYPE_RAMDISK        =0x00000004
        BCDE_DEVICE_TYPE_UNKNOWN        =0x00000005

        BCD_COPY_CREATE_NEW_OBJECT_IDENTIFIER = 0x00000001

        BCDE_VISTA_OS_ENTRY = 0x10200003
        BCDE_LEGACY_OS_ENTRY = 0x10300006

        BCDE_LIBRARY_TYPE_APPLICATIONPATH = \
            MAKE_BCDE_DATA_TYPE(BCDE_CLASS.LIBRARY, BCDE_FORMAT.STRING, 0x000002)
        # Get the current boot loader GUID
        w = wmi.WMI(computer=".", impersonation_level="Impersonate", privileges=("Backup", "Restore"), namespace="WMI", suffix="BcdStore")
        success, store = w.OpenStore("")
        if success is True:
            # Have to convert to wmi object
            store = wmi._wmi_object(store)

        # Get the bootmgr (yes - obj first)
        b_mgr, success = store.OpenObject("{9dea862c-5cdd-4e70-acc1-f32b344d4795}")
        if success is True:
            # Have to convert to wmi object
            b_mgr = wmi._wmi_object(b_mgr)
        
        # Get all boot loader objects
        obj_list, success = store.EnumerateObjects(0)
        if success is True:
            obj_list = wmi._wmi_object(obj_list)

        w.close()


        # Rebuild BCD Database
        cmd = "%SystemRoot%\\System32\\bcdboot c:\\windows /m " + boot_loader_guid + " /f ALL" #UEFI"
        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=3, require_return_code=0)
        #p(str(returncode) + " - " + output)
        if returncode == -2:
            # Error running command?
            p("}}rbError - get boot options!}}xx\n" + output)
            return False
        

        return True
    
    @staticmethod
    def rebuild_bcd_data_cmd_line():

        # Rebuild BCD Database
        cmd = "%SystemRoot%\\System32\\bcdboot c:\\windows"
        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=3, require_return_code=0)
        #p(str(returncode) + " - " + output)
        if returncode == -2:
            # Error running command?
            p("}}rbError - bcdboot failed!}}xx\n" + output)
            return False

        return True

    @staticmethod
    def lock_boot_settings():
        ret = True

        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping lock_boot_settings policy}}xx")
            return True

        # Make sure bootim.exe is disabled (the blue screen menu) This will block recovery options
        #New-Item -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bootim.exe"
        #Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\bootim.exe" -Name "Debugger" -Type "String" -Value "taskill /F /IM bootim.exe" -Force
        RegistrySettings.set_reg_value(
            root="HKLM",
            app="Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options",
            subkey="bootim.exe",
            value_name="Debugger",
            value="taskill /F /IM bootim.exe",
            value_type="REG_SZ")

        # Rewrite UEFI values
        # TODO - Need more debugging before using in production
        #FolderPermissions.update_uefi_boot_order()
        # TODO - Need more debugging before using in production
        #FolderPermissions.rebuild_bcd_data_cmd_line()

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
            ("%SystemRoot%\\system32\\bcdedit.exe /deletevalue \"{current}\" recoverysequence ", None),

            ("%SystemRoot%\\System32\\bcdedit.exe /timeout 0", 0),
            # Set in uefi area
            #("%SystemRoot%\\System32\\bcdedit.exe /set \"{fwbootmgr}\" timeout 0", None),
            
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{bootmgr}\" displaybootmenu no", 0),
            # Use standard policy - no F8 key
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" bootmenupolicy Standard", 0),
            # Try to boot normally every time - helps to not show recovery options
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" bootstatuspolicy ignoreallfailures", 0),
            # Disable recovery
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" recoveryenabled off", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{globalsettings}\" recoveryenabled off", 0),
            # Disable Advanced Options
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" advancedoptions off", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{globalsettings}\" advancedoptions off", 0),

            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" bootems off", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" optionsedit off", 0),

            # disable Win Recovery Environment (WinRE)
            ("%SystemRoot%\\system32\\reagentc /disable", None),

            ("%SystemRoot%\\system32\\bcdedit.exe /deletevalue \"" + boot_identifier + "\" safeboot ", None),

            # Set boot UEFI boot order so hard disk is first
            #("%SystemRoot%\\system32\\bcdedit.exe /set \"{bootmgr}\" displayorder \"" + boot_identifier + "\"", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{bootmgr}\" displayorder \"" + boot_identifier + "\" /addfirst", 0),
            
            #("%SystemRoot%\\system32\\bcdedit.exe /set \"{fwbootmgr}\" displayorder \"{bootmgr}\"", None),
            #("%SystemRoot%\\system32\\bcdedit.exe /set \"{fwbootmgr}\" displayorder \"{bootmgr}\" /addfirst", None),
            #("%SystemRoot%\\system32\\bcdedit.exe /set \"{fwbootmgr}\" displayorder \"{bootmgr}\"", None),
            #("%SystemRoot%\\system32\\bcdedit.exe /set \"{fwbootmgr}\" displayorder \"{bootmgr}\"", None),
            # TODO - boot setting still not taking in nvram?
            #("%SystemRoot%\\system32\\bcdboot.exe %windir%", 0),
            #("%SystemRoot%\\system32\\mountvol.exe  s: /s", None),
            #("%SystemRoot%\\system32\\bcdboot.exe %SystemRoot% /s s: /F UEFI", None),
            #("%SystemRoot%\\system32\\mountvol.exe  s: /D", None),
            #mountvol s: /S
            #bcdboot c:\windows /s s: /F UEFI
            #mountvol s: /D
        ]

        for tcmd in cmds:
            cmd = tcmd[0]
            require_return_code = tcmd[1]
            cmd = os.path.expandvars(cmd)
            returncode, output = ProcessManagement.run_cmd(cmd,
                attempts=3, require_return_code=require_return_code)
            fail_ok = ""
            if require_return_code is None:
                fail_ok = " (ok if this fails) "
            p(str(returncode) + " - " + fail_ok + output, log_level=4)
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
    def enable_uefi_pxe_boot():
        # Enable PXE boot option to image the server

        return True

    @staticmethod
    def disable_uefi_alt_boot():
        # Set boot options to disabled if they aren't our windows boot option
        return True

    @staticmethod
    def update_uefi_boot_partition():
        from mgmt_Computer import Computer
        # Find the current windows boot entry and make sure the GPT partition is correct
        with privileges():
            try:
                verify_uefi_firmware()
            except:
                p("}}gnNOT UEFI BIOS!}}xx", log_level=3)
                return True
            
            # Get the list of disks
            # https://stackoverflow.com/questions/56784915/python-wmi-can-we-really-say-that-c-is-always-the-boot-drive
            w = Computer.get_wmi_connection(namespace='root/Microsoft/Windows/Storage')
            drives = w.MSFT_Disk() #w.Win32_DiskDrive()
            
            part_info = None
            for drive in drives:
                # print(r)
                disk_number = drive.Number # r.Index
                # physical_path = r'\\.\PHYSICALDRIVE' + str(disk_number)  # r.DeviceID
                
                # Get partitions for this drive if it is the boot drive
                if drive.IsBoot == True:
                    partitions = drive.associators("MSFT_DiskToPartition")
                    for part in partitions:
                        if part.GptType == "{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}":
                            # Found EFI partition
                            sector_size = int(drive.PhysicalSectorSize)
                            part_starting_sector = int(int(part.Offset) / sector_size)
                            part_size = int(int(part.Size) / sector_size)
                            part_guid = part.Guid
                            part_number = part.PartitionNumber
                            part_info = (part, part_guid, part_number, part_starting_sector, part_size)
                            break

            if part_info is None:
                # Couldn't find EFI partition!
                p("}}gnUEFI - Couldn't find system EFI partition!}}xx", log_level=3)
                return False
            
            # Create the device path list for windows boot manager
            bootmgr_path_list = DevicePathList()
            bootmgr_path_list.paths = []  # Make sure we clear out any default stuff
            # Calculate path data we need
            #part_info = (part, part_guid, part_number, part_starting_sector, part_size)
            # Get in RFC4122 binary encoded format (first half in different endian mode?)
            packed_guid = uuid.UUID(part_info[1]).bytes_le
            WIN_HARD_DRIVE_MEDIA_PATH = struct.Struct("<LQQ16sBB").pack(
                part_info[2],             # Long - 4  bytes
                part_info[3],             # long long - 8 bytes
                part_info[4],             # long long - 8 bytes
                packed_guid,              # 16 bytes, 
                0x02,                     # 1 byte - 0x01 for mbr, 0x02 for gpt
                0x02,                     # 1 byte - 0x00 none, 0x01 mbr, 0x02 gpt
            )

            WIN_DEVICE_PATH_DATA = string_to_utf16_bytes("\\EFI\\Microsoft\\Boot\\bootmgfw.efi")

            # Add the disk GUID entry
            bootmgr_path_list.paths.append(DevicePath(
                DevicePathType.MEDIA_DEVICE_PATH, MediaDevicePathSubtype.HARD_DRIVE, WIN_HARD_DRIVE_MEDIA_PATH
                )
            )
            # Add the file path
            bootmgr_path_list.paths.append(DevicePath(
                DevicePathType.MEDIA_DEVICE_PATH, MediaDevicePathSubtype.FILE_PATH, WIN_DEVICE_PATH_DATA
                )
            )
            bootmgr_path_list.paths.append(DevicePath(
                DevicePathType.END_OF_HARDWARE_DEVICE_PATH, EndOfHardwareDevicePathSubtype.END_ENTIRE_DEVICE_PATH
            ))

            # Get the current boot item
            curr_boot_index, attr = get_variable("BootCurrent")
            # Convert from bytes to a integer value
            curr_boot_index = struct.unpack("<h", curr_boot_index)[0]

            # Adjust the current boot item to point to the proper partition
            try:
                boot_entry = get_parsed_boot_entry(curr_boot_index)

                #boot_entry.attributes = LoadOptionAttributes.LOAD_OPTION_ACTIVE
                boot_entry.device_path_list = bootmgr_path_list
                set_parsed_boot_entry(curr_boot_index, boot_entry)
            except Exception as ex:
                # Will get errors if we run out of entries. That is OK.
                if "environment option" not in str(ex):
                    p("}}rbError: }}xx" + str(ex))
                    #traceback.print_exc()
                pass

        return True

    @staticmethod
    def update_uefi_boot_order():
        from mgmt_Computer import Computer

        # NOTE - Likely need to rebuild BCD after this!

        # Elevate privileges for reading/writing uefi values
        with privileges():
            try:
                verify_uefi_firmware()
            except:
                p("}}gnNOT UEFI BIOS!}}xx", log_level=3)
                return True

            # Get the list of disks
            # https://stackoverflow.com/questions/56784915/python-wmi-can-we-really-say-that-c-is-always-the-boot-drive
            w = Computer.get_wmi_connection(namespace='root/Microsoft/Windows/Storage')
            drives = w.MSFT_Disk() #w.Win32_DiskDrive()
            
            part_info = None
            for drive in drives:
                # print(r)
                disk_number = drive.Number # r.Index
                # physical_path = r'\\.\PHYSICALDRIVE' + str(disk_number)  # r.DeviceID
                
                # Get partitions for this drive if it is the boot drive
                if drive.IsBoot == True:
                    partitions = drive.associators("MSFT_DiskToPartition")
                    for part in partitions:
                        if part.GptType == "{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}":
                            # Found EFI partition
                            sector_size = int(drive.PhysicalSectorSize)
                            part_starting_sector = int(int(part.Offset) / sector_size)
                            part_size = int(int(part.Size) / sector_size)
                            part_guid = part.Guid
                            part_number = part.PartitionNumber
                            part_info = (part, part_guid, part_number, part_starting_sector, part_size)
                            break

            if part_info is None:
                # Couldn't find EFI partition!
                p("}}gnUEFI - Couldn't find system EFI partition!}}xx", log_level=3)
                return False
            
            # Create the device path list for windows boot manager
            bootmgr_path_list = DevicePathList()
            bootmgr_path_list.paths = []  # Make sure we clear out any default stuff
            # Calculate path data we need
            #part_info = (part, part_guid, part_number, part_starting_sector, part_size)
            # Get in RFC4122 binary encoded format (first half in different endian mode?)
            packed_guid = uuid.UUID(part_info[1]).bytes_le
            WIN_HARD_DRIVE_MEDIA_PATH = struct.Struct("<LQQ16sBB").pack(
                part_info[2],             # Long - 4  bytes
                part_info[3],             # long long - 8 bytes
                part_info[4],             # long long - 8 bytes
                packed_guid,              # 16 bytes, 
                0x02,                     # 1 byte - 0x01 for mbr, 0x02 for gpt
                0x02,                     # 1 byte - 0x00 none, 0x01 mbr, 0x02 gpt
            )

            WIN_DEVICE_PATH_DATA = string_to_utf16_bytes("\\EFI\\Microsoft\\Boot\\bootmgfw.efi")

            # Add the disk GUID entry
            bootmgr_path_list.paths.append(DevicePath(
                DevicePathType.MEDIA_DEVICE_PATH, MediaDevicePathSubtype.HARD_DRIVE, WIN_HARD_DRIVE_MEDIA_PATH
                )
            )
            # Add the file path
            bootmgr_path_list.paths.append(DevicePath(
                DevicePathType.MEDIA_DEVICE_PATH, MediaDevicePathSubtype.FILE_PATH, WIN_DEVICE_PATH_DATA
                )
            )
            bootmgr_path_list.paths.append(DevicePath(
                DevicePathType.END_OF_HARDWARE_DEVICE_PATH, EndOfHardwareDevicePathSubtype.END_ENTIRE_DEVICE_PATH
            ))

            # Get the current boot item
            curr_boot_index, attr = get_variable("BootCurrent")
            # Convert from bytes to a integer value
            curr_boot_index = struct.unpack("<h", curr_boot_index)[0]

            # Adjust the current boot item to point to the proper partition
            try:
                boot_entry = get_parsed_boot_entry(curr_boot_index)

                #boot_entry.attributes = LoadOptionAttributes.LOAD_OPTION_ACTIVE
                boot_entry.device_path_list = bootmgr_path_list
                set_parsed_boot_entry(curr_boot_index, boot_entry)
            except Exception as ex:
                # Will get errors if we run out of entries. That is OK.
                if "environment option" not in str(ex):
                    p("}}rbError: }}xx" + str(ex))
                    #traceback.print_exc()
                pass
            
            # Make sure we push this item to the top of the boot order
            # Get current boot order
            curr_boot_order = get_boot_order()
            new_boot_order = []
            new_boot_order.append(curr_boot_index)
            for item in curr_boot_order:
                if item != curr_boot_index:
                    new_boot_order.append(item)
            set_boot_order(new_boot_order)

            # Disable all other boot options by hiding them?
            for i in range(0, 24):
                try:
                    if i == curr_boot_index:
                        # Skip the current boot entry
                        pass
                    else:
                        boot_entry = get_parsed_boot_entry(i)
                        boot_entry.attributes = LoadOptionAttributes.LOAD_OPTION_HIDDEN | LoadOptionAttributes.LOAD_OPTION_ACTIVE
                        set_boot_entry(i, boot_entry)
                except Exception as ex:
                    # Will get errors if we run out of entries. That is OK.
                    if "environment option" not in str(ex):
                        p("}}rbError: }}xx" + str(ex))
                        #traceback.print_exc()
                    pass
            
            # Set timeout to 0
            set_variable("Timeout", 0)
            # Make sure we don't boot to something else later
            delete_variable("BootNext")
            
        return True

    @staticmethod
    def enable_pxe_boot():
        return False

    @staticmethod
    def unlock_boot_settings():
        ret = True

        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping unlock_boot_settings}}xx")
            return True

        # Unblock bootim (recovery screen stuff)
        RegistrySettings.remove_key("HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\bootim.exe")
        
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
        #if "{default}" in output:
        #    boot_identifier = "{default}"

        p("}}gnBoot ID: " + boot_identifier + "}}xx", log_level=4)

        cmds = [
            ("%SystemRoot%\\System32\\bcdedit.exe /timeout 30", 0),
            
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{bootmgr}\" displaybootmenu yes", 0),
            # Use standard policy - no F8 key
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" bootmenupolicy Standard", 0),
            # Try to boot normally every time - helps to not show recovery options
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" bootstatuspolicy IgnoreShutdownFailures", 0),
            # Disable recovery
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" recoveryenabled on", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{globalsettings}\" recoveryenabled on", 0),
            # Disable Advanced Options
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" advancedoptions on", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"{globalsettings}\" advancedoptions on", 0),

            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" bootems on", 0),
            ("%SystemRoot%\\system32\\bcdedit.exe /set \"" + boot_identifier + "\" optionsedit on", 0),

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
        
        return ret
    
    @staticmethod
    def disable_volume_shadow_copies():
        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping disable volume shadow copies}}xx")
            return True
        
        # Make sure SAM isn't readable: https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36934
        cmd = "icacls %windir%\\system32\\config\\*.* /inheritance:e"

        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=1, require_return_code=None, cmd_timeout=300)
        
        cmd = "vssadmin delete shadows /for=c: /all /Quiet"

        cmd = os.path.expandvars(cmd)
        returncode, output = ProcessManagement.run_cmd(cmd,
            attempts=1, require_return_code=None, cmd_timeout=300)
        
        return True
      

if __name__ == "__main__":
    p("Testing:")
    ret = FolderPermissions.lock_boot_settings()
    p("Return: "  + str(ret))
    