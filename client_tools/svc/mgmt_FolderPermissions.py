
# Needed for folder security
import win32security
import win32api
import ntsecuritycon
import win32net
import ctypes

import sys
import os
import traceback

import util

from color import p


class FolderPermissions:
    # Class to deal with folder permissions
    
    GROUP_EVERYONE = None
    GROUP_ADMINISTRATORS = None
    CURRENT_USER = None
    SYSTEM_USER = None

    @staticmethod
    def is_admin():
        ret = False
        r = ctypes.windll.shell32.IsUserAnAdmin()
        if r == 1:
            ret = True
        
        return ret

    @staticmethod
    def is_in_admin_group():
        # Get the list of groups for this user - if not in admin, return false
        ret = False
        
        try:
            server_name = None  # None for local machine
            user_name = win32api.GetUserName()
            if user_name == "SYSTEM":
                # SYSTEM user counts!
                return True

            # p("}}ynChecking Admin Membership for: " + user_name)
            groups = win32net.NetUserGetLocalGroups(server_name, user_name, 0)

            for g in groups:
                if g.lower() == "administrators":
                    ret = True
        except Exception as ex:
            p("}}rnERROR - Unknown Error! \n" + str(ex))
            ret = False

        return ret
    
    @staticmethod
    def init_win_user_accounts():
        # Load account information for groups/users
        
        if FolderPermissions.GROUP_EVERYONE is None:
            EVERYONE, domain, type = win32security.LookupAccountName("", "Everyone")
            FolderPermissions.GROUP_EVERYONE = EVERYONE
            
        if FolderPermissions.GROUP_ADMINISTRATORS is None:
            ADMINISTRATORS, domain, type = win32security.LookupAccountName("", "Administrators")
            FolderPermissions.GROUP_ADMINISTRATORS = ADMINISTRATORS
        
        if FolderPermissions.CURRENT_USER is None:
            CURRENT_USER, domain, type = win32security.LookupAccountName("", win32api.GetUserName())
            
            if CURRENT_USER is None:
                try:
                    CURRENT_USER, domain, type = win32security.LookupAccountName("", "huskers")
                except:
                    CURRENT_USER = None
                if CURRENT_USER is None:
                    try:
                        CURRENT_USER, domain, type = win32security.LookupAccountName("", "ray")
                    except:
                        CURRENT_USER = None
            FolderPermissions.CURRENT_USER = CURRENT_USER
        
        if FolderPermissions.SYSTEM_USER is None:
            SYSTEM_USER, domain, type = win32security.LookupAccountName("", "System")
            FolderPermissions.SYSTEM_USER = SYSTEM_USER



    @staticmethod
    def show_cacls(filename):
        print("\n\n")    
        for line in os.popen("cacls %s" % filename).read().splitlines():
            print(line)
    
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
    def set_default_ope_folder_permissions():
        # Set permissions on OPE folder so inmates can't change things
        
        # Load up the system goups/users
        FolderPermissions.init_win_user_accounts()
        
        # Make sure folders exits
        if not os.path.isdir(util.ROOT_FOLDER):
            os.makedirs(util.ROOT_FOLDER, exist_ok=True)
        if not os.path.isdir(util.TMP_FOLDER):
            os.makedirs(util.TMP_FOLDER, exist_ok=True)
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
        # Make sure the ope-sshot.log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "ope-sshot.log")):
            f = open(os.path.join(util.LOG_FOLDER, "ope-sshot.log"), "w")
            f.close()
        
        # ---- ope-mgmt.log ----
        # Make sure the ope-sshot.log file exists so we can set permissions on it later
        if not os.path.isfile(os.path.join(util.LOG_FOLDER, "ope-mgmt.log")):
            f = open(os.path.join(util.LOG_FOLDER, "ope-mgmt.log"), "w")
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
            util.SCREEN_SHOTS_FOLDER: "c",
            
        }
        
        for f in app_folders.keys():
            everyone_rights = app_folders[f]
            p("}}gnSetting permissions on " + f + " (rights for everyone " + everyone_rights + ")}}xx")
            FolderPermissions.set_ope_folder_permissions(f, everyone_rights=everyone_rights)

        return
      

if __name__ == "__main__":
    print("Testing:")
    print(FolderPermissions.is_in_admin_group())