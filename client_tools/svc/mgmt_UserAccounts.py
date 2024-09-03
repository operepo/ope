import pyad.pyad
import win32api
import win32con
import win32security
import win32process
import win32ts
import win32profile
import ctypes
import win32netcon
import ntsecuritycon
import win32net
import wmi
import traceback
import shutil
import random
import os
import pyad

# Need this for winsys exceptions
import winsys
from winsys import accounts
from color import p
import util

from mgmt_RegistrySettings import RegistrySettings
from mgmt_Computer import Computer


class UserAccounts:

    # All student accounts get added to this group
    STUDENTS_GROUP = "OPEStudents"
    ADMINS_GROUP = "OPEAdmins"
    
    GROUP_EVERYONE = None
    GROUP_ADMINISTRATORS = None
    CURRENT_USER = None
    SYSTEM_USER = None

    DISABLE_ACCOUNT_FLAGS = win32netcon.UF_SCRIPT | win32netcon.UF_ACCOUNTDISABLE | \
            win32netcon.UF_PASSWD_CANT_CHANGE | win32netcon.UF_DONT_EXPIRE_PASSWD
    ENABLE_ACCOUNT_FLAGS = win32netcon.UF_NORMAL_ACCOUNT | win32netcon.UF_PASSWD_CANT_CHANGE | \
            win32netcon.UF_DONT_EXPIRE_PASSWD | win32netcon.UF_SCRIPT

    #service_account = accounts.principal (accounts.WELL_KNOWN_SID.Service)
    #local_admin = accounts.principal ("Administrator")
    #domain_users = accounts.principal (r"DOMAIN\Domain Users")

    # Invalid session ID for WTS
    WTS_INVALID_SESSION_ID = 0xffffffff
    #TS State Enum
    WTSActive = 0
    WTSConnected = 1
    WTSConnectQuery = 2
    WTSShadow = 3
    WTSDisconnected = 4
    WTSIdle = 5
    WTSListen = 6
    WTSReset = 7
    WTSDown = 8
    WTSInit = 9


    @staticmethod
    def allow_group_to_logon_locally(group_name="OPEAdmins"):

        try:
            # Get the SID for the group
            sid, domain, account_type = win32security.LookupAccountName(None, group_name)

            # Get local security policy
            lsa = win32security.LsaOpenPolicy(None, win32security.POLICY_ALL_ACCESS)

            # We want to add the following right to the group
            right = "SeInteractiveLogonRight"

            # Add right
            win32security.LsaAddAccountRights(lsa, sid, [right])

            # Close the handle
            win32security.LsaClose(lsa)

            p("}}gb" + f"{group_name} has been granted the 'Allow logon locally' right." + "}}xx")
        except Exception as ex:
            p("}}rb" + f"Error granting 'Allow logon locally' right to {group_name} - {ex}" + "}}xx")
            return False

        return True

    @staticmethod
    def remove_group_from_logon_locally(group_name="OPEAdmins"):
        try:
            # Get the SID for the group
            sid, domain, account_type = win32security.LookupAccountName(None, group_name)
            #p("SID: " + str(sid))

            # Get local security policy
            lsa = win32security.LsaOpenPolicy(None, win32security.POLICY_ALL_ACCESS)

            # We want to add the following right to the group
            right = "SeInteractiveLogonRight"

            # Add right
            win32security.LsaRemoveAccountRights(lsa, sid, False, [right])  # True would remove all rights from object

            # Close the handle
            win32security.LsaClose(lsa)

            p("}}gb" + f"{group_name} has been removed from the 'Allow logon locally' right." + "}}xx")
        except Exception as ex:
            if "lookupaccountname" in str(ex).lower():
                p("}}yn" + f"Group '{group_name}' not in 'Allow Logon Locally' - skipping removal." + "}}xx")
                return True
            p("}}rb" + f"Error removing 'Allow logon locally' right from {group_name} - {ex}" + "}}xx")
            return False

        return True

    @staticmethod
    def get_current_user():
        return win32api.GetUserName()
    
    @staticmethod
    def get_active_user_name():
        user_name = ""
        user_token = UserAccounts.get_active_user_token()
        
        if user_token is None:
            # Unable to pull active user, no one logged in?
            return ""

        # Translate to SID
        sidObj, intVal = win32security.GetTokenInformation(user_token, win32security.TokenUser)
        if sidObj:
            accountName, domainName, accountTypeInt = win32security.LookupAccountSid(".", sidObj)
            #p("}}gnRunning As: " + accountName + "}}xx", debug_level=2)
            p("}}gnRunning As: " + domainName + "\\" + accountName + "}}xx")
            user_name = domainName + "\\" + accountName
        else:
            p("}}rnUnable to get User Token! }}xx", debug_level=1)
            return ""
        #p("}}gnFound User Token: " + str(user_token) + "}}xx", debug_level=5)
        user_token.close()

        if domainName is None or accountTypeInt is None or intVal is None:
            # Make pylint shutup
            pass

        return user_name
    
    @staticmethod
    def get_user_token(user_name):
        ret = None
        try:
            ret = accounts.principal(user_name)
        except Exception as ex:
            p("Exception: " + str(ex) + " - " + traceback.format_exc())

        return ret

    @staticmethod
    def get_active_user_token():
        # Figure out the active user token we need to use to run the app as
        ret = None

        # Get the current user name
        user_name = win32api.GetUserName()

        if user_name != "SYSTEM":
            # Running as a logged in user, get the current users token
            current_process = win32process.GetCurrentProcess()
            token = win32security.OpenProcessToken(current_process,
                win32con.MAXIMUM_ALLOWED)
                # win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY)  #

            ret = token

            return ret

        #if user_name == "SYSTEM":
        #    p("}}gnStarted by SYSTEM user (OPEService) - trying to switch user identity}}xx")

        # Get a list of Terminal Service sessions and see which one is active
        active_session = UserAccounts.WTS_INVALID_SESSION_ID
        station_name = ""
        sessions = win32ts.WTSEnumerateSessions(None, 1, 0)

        if station_name is None:
            # make pylint shut up
            pass
        
        for session in sessions:
            # or session['State'] == UserAccounts.WTSConnected
            if session['State'] == UserAccounts.WTSActive:
                # Found the active session
                active_session = session['SessionId']
                station_name = session["WinStationName"]

        # If we didn't find one, try this way
        if active_session == UserAccounts.WTS_INVALID_SESSION_ID:
            active_session = win32ts.WTSGetActiveConsoleSessionId()
        if active_session == UserAccounts.WTS_INVALID_SESSION_ID:
                # User not logged in right now? or lock screen up?
                p("}}gnNo console user or desktop locked}}xx", log_level=1)
                return ret
            
        # Get the current console session
        #p("Got Console: " + str(active_session), debug_level=5)

        # Login to the terminal service to get the user token for the console id so we can impersonate it
        try:
            #svr = win32ts.WTSOpenServer(".")
            #win32ts.WTSCloseServer(svr)
            user_token = win32ts.WTSQueryUserToken(active_session)

             # Copy the token so we can modify it
            user_token_copy = win32security.DuplicateTokenEx(user_token,
                                                    win32security.SecurityImpersonation,
                                                    win32security.TOKEN_ALL_ACCESS,
                                                    win32security.TokenPrimary)

            ret = user_token_copy
            user_token.close()
        except Exception as ex:
            p("}}rnUnknown Error - trying to get WTS UserToken\n" + str(ex) + "}}xx", debug_level=1)
            return ret
        
        #p("User Token Found " + str(user_token_copy), debug_level=5)

        return ret

    @staticmethod
    def get_current_login_sessions():
        # Get a list of users that are logged in
        ret = []

        # Get the current user name
        # Shouldn't need this as WTSEnumerateSessions should get all users currently logged in
        # curr_user = win32api.GetUserName()
        # if UserAccounts.is_user_in_group(curr_user, "OPEStudents"):
        #     ret.append((domain, curr_user))

        # Get the list of users from WTS
        wts_sessions = []
        sessions = win32ts.WTSEnumerateSessions(None, 1, 0)
        
        for session in sessions:
            # Ignore listen status(no user for that), all others query
            if session['State'] == UserAccounts.WTSActive or \
                session['State'] == UserAccounts.WTSDisconnected or \
                session['State'] == UserAccounts.WTSConnected:
                # Found the active session
                #active_session = session['SessionId']
                #station_name = session["WinStationName"]
                wts_sessions.append(session['SessionId'])
        
        # Get the console session (duplicate?)
        active_session = win32ts.WTSGetActiveConsoleSessionId()
        if active_session is not None and active_session != UserAccounts.WTS_INVALID_SESSION_ID:
            wts_sessions.append(active_session)
        
        # Convert sessions to users and check their group membership
        for session in wts_sessions:
            user_name = win32ts.WTSQuerySessionInformation(None, session, win32ts.WTSUserName)
            domain = win32ts.WTSQuerySessionInformation(None, session, win32ts.WTSDomainName)
            #p("}}gnChecking Session: " + domain + "\\" + user_name + "}}xx", debug_level=4)
            if user_name is not None and user_name != "":
                ret.append((domain, user_name))
                
        return ret
    
    @staticmethod
    def get_student_login_sessions():
        # Get a list of students that are logged in
        ret = []

        sessions = UserAccounts.get_current_login_sessions()
        for session in sessions:
            user_name = session[0] + "\\" + session[1]
            p("}}gnChecking Session: " + user_name + "}}xx", debug_level=4)
            if UserAccounts.is_user_in_group(user_name, "OPEStudents"):
                ret.append(session)

        return ret

    @staticmethod
    def is_uac_admin():
        ret = False
        r = ctypes.windll.shell32.IsUserAnAdmin()
        if r == 1:
            ret = True
        
        return ret

    @staticmethod
    def is_in_admin_group(user_name=None):
        # Get the list of groups for this user - if not in admin, return false
        ret = False
        
        try:
            server_name = None  # None for local machine
            if user_name is None:
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
            p("}}rnERROR - Unknown Error! }}xx\n" + str(ex))
            ret = False

        return ret

    @staticmethod
    def is_user_in_group(user_name, group_name):
        ret = False

        try:
            server_name = None  # for local machine
            groups = win32net.NetUserGetLocalGroups(server_name, user_name, 0)

            for g in groups:
                if g.lower() == group_name.lower():
                    # Found group!
                    ret = True
                    break   # Break out of loop

        except Exception as ex:
            p("}}rnERROR - Unknown Error trying to get groups for user! (" + user_name + "/" + group_name + ")}}xx" + \
                str(ex))
            return None
        return ret

    @staticmethod
    def elevate_process_privilege_to_debug():
        #add_privilege=ntsecuritycon.SE_RESTORE_NAME | 
        #ntsecuritycon.SE_BACKUP_NAME ):
        try:
            se_debug_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_DEBUG_NAME)
            
            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [
                    (se_debug_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
                ]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate debug privileges}}xx\n" +
                str(ex))
            return False

        return True

    @staticmethod
    def elevate_process_privilege_to_backup_restore():
        #add_privilege=ntsecuritycon.SE_RESTORE_NAME | 
        #ntsecuritycon.SE_BACKUP_NAME ):
        try:
            se_backup_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_BACKUP_NAME)
            se_restore_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_RESTORE_NAME)

            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [(se_backup_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
                    (se_restore_value, ntsecuritycon.SE_PRIVILEGE_ENABLED)]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate backup/restore privileges}}xx\n" +
                str(ex))
            return False

        return True
    
    @staticmethod
    def elevate_process_privilege_to_se_security_name():
        #add_privilege=ntsecuritycon.SE_RESTORE_NAME | 
        #ntsecuritycon.SE_BACKUP_NAME ):
        try:
            se_security_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_SECURITY_NAME)

            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [(se_security_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
                    ]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate backup/restore privileges}}xx\n" +
                str(ex))
            return False

        return True

    @staticmethod
    def elevate_process_privilege_to_tcb():
        try:
            se_tcb_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_TCB_NAME)

            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [
                (se_tcb_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
            ]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate tcb privileges}}xx\n" +
                str(ex))
            return False

        return True

    @staticmethod
    def elevate_process_privilege_to_shutdown():
        try:
            se_shutdown_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_SHUTDOWN_NAME)

            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [
                (se_shutdown_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
            ]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate SE_SHUTDOWN privileges}}xx\n" +
                str(ex))
            return False

        return True
    
    @staticmethod
    def elevate_process_privilege_to_take_ownership():
        try:
            se_take_ownership_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_TAKE_OWNERSHIP_NAME)

            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [
                (se_take_ownership_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
            ]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate SE_TAKE_OWNERSHIP privileges}}xx\n" +
                str(ex))
            return False

        return True
    
    @staticmethod
    def elevate_process_privilege_assign_primary_token():
        try:
            se_assignprimarytoken_value = win32security.LookupPrivilegeValue(None, ntsecuritycon.SE_ASSIGNPRIMARYTOKEN_NAME)

            flags = ntsecuritycon.TOKEN_ADJUST_PRIVILEGES \
                | ntsecuritycon.TOKEN_QUERY
            
            proces_token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)

            # Add backup/restore privileges
            new_privs = [
                (se_assignprimarytoken_value, ntsecuritycon.SE_PRIVILEGE_ENABLED),
            ]

            win32security.AdjustTokenPrivileges(proces_token, 0, new_privs)
        except Exception as ex:
            p("}}rbException - trying to elevate assignprimarytoken privileges}}xx\n" +
                str(ex))
            return False

        return True
    
    @staticmethod
    def generate_random_password():
        ret = ""

        # Get one upper case
        ret += chr(random.randint(65,90))
        # Get one lower case
        ret += chr(random.randint(97, 122)) 
        # get one number
        ret += chr(random.randint(48,57))

        # get one symbol
        ret += chr(random.randint(58,64))
        # 7 randoms
        for i in range(1,7):
            ret += chr(random.randint(35,125))
            if i is None:
                # make pylint shutup
                pass

        # Don't use \ or ' or " charcters
        ret = ret.replace("'", "").replace("\"", "").replace("\\", "")
        return ret

    @staticmethod
    def create_local_student_account(user_name=None, full_name=None, password=None):
        # Command that is run to start this function
        only_for = "create_student_account"

        ret = True
        # Make sure we have parameters
        if user_name is None:
            user_name = util.get_param(2, None, only_for=only_for)
        if full_name is None:
            full_name = util.get_param(3, None, only_for=only_for)
        if password is None:
            password = util.get_param(4, None, only_for=only_for)
        if user_name is None or full_name is None or password is None:
            p("}}rbError - Invalid parameters to create new student user!}}xx", debug_level=1)
            return False

        # Create local student account
        try:
            p("}}yn\tAdding student account (" + user_name + ")...}}xx")
            accounts.User.create(user_name, password)
        # except pywintypes.error as ex:
        except Exception as ex:
            if ex.args[2] == "The account already exists.":
                pass
            else:
                # Unexpected error
                p("}}rb" + str(ex) + "}}xx")
                ret = False

        # Set info for the student
        user_data = dict()
        user_data['name'] = user_name
        user_data['full_name'] = full_name
        # Start w a random complex password
        user_data['password'] = UserAccounts.generate_random_password()  # password
        # NOTE - Student accounts are always created disabled!
        user_data['flags'] = UserAccounts.DISABLE_ACCOUNT_FLAGS
        user_data['priv'] = win32netcon.USER_PRIV_USER
        user_data['comment'] = 'OPE Student Account'
        # user_data['home_dir'] = home_dir
        # user_data['home_dir_drive'] = "h:"
        user_data['primary_group_id'] = ntsecuritycon.DOMAIN_GROUP_RID_USERS
        user_data['password_expired'] = 0
        user_data['acct_expires'] = win32netcon.TIMEQ_FOREVER
        
        win32net.NetUserSetInfo(None, user_name, 3, user_data)

        # Make sure the password is complex enough
        tmp_password = password
        if len(tmp_password) < 8:
            p("}}rbStudent Password Too Short! Padding with !s to 8 characters}}xx")
            pad_chars = (8-len(tmp_password)) * "!"
            tmp_password += pad_chars
        # Set the password
        try:
            user_data['password'] = tmp_password
            win32net.NetUserSetInfo(None, user_name, 3, user_data)
        except Exception as ex:
            p("}}rbERROR setting password for " + user_name + "}}xx\n" + str(ex))

        # Add student to the students group
        p("}}yn\tAdding student to students group...}}xx")
        if not UserAccounts.set_default_groups_for_student(user_name):
            ret = False
        
        return ret

    @staticmethod
    def create_local_admin_account(user_name, full_name, password):
        # Create local admin account
        ret = True
                
        try:
            p("}}yn\tAdding Admin account (" + user_name + ")...}}xx")
            accounts.User.create(user_name, password)
            # p("}}yn\t\tDone.}}xx")
        # except pywintypes.error as ex:
        except Exception as ex:
            if ex.args[2] == "The account already exists.":
                pass
            else:
                # Unexpected error
                p("}}rb" + str(ex) + "}}xx")
                ret = False

        user_data = dict()
        user_data['name'] = user_name
        user_data['full_name'] = full_name
        #user_data['password'] = UserAccounts.generate_random_password()
        user_data['flags'] = UserAccounts.ENABLE_ACCOUNT_FLAGS
        user_data['priv'] = win32netcon.USER_PRIV_ADMIN
        user_data['comment'] = 'OPE Admin Account'
        # user_data['home_dir'] = home_dir
        # user_data['home_dir_drive'] = "h:"
        user_data['primary_group_id'] = ntsecuritycon.DOMAIN_GROUP_RID_USERS
        user_data['password_expired'] = 0
        user_data['acct_expires'] = win32netcon.TIMEQ_FOREVER
        
        win32net.NetUserSetInfo(None, user_name, 3, user_data)

        # Set password
        try:
            user_data['password'] = password
            win32net.NetUserSetInfo(None, user_name, 3, user_data)
        except Exception as ex:
            p("}}rbERROR setting password for " + user_name + "}}xx\n" + str(ex))
        
        if not UserAccounts.set_default_groups_for_admin(user_name):
            ret = False

        return ret
    
    @staticmethod
    def set_group_description(group_name, description, server=None):
        # Server - None for local computer, or domain controller
        
        # Fetch the current group information
        try:
            group_info = win32net.NetLocalGroupGetInfo(server, group_name, 1)
        except win32net.error as e:
            p("}}rbError fetching group info: " + group_name + " - " + str(e) + "}}xx")
            return False

        # Update the group description
        group_info['comment'] = description

        # Set the updated group information
        try:
            win32net.NetLocalGroupSetInfo(server, group_name, 1, group_info)
        except win32net.error as e:
            p("}}rbError setting group info: " + group_name + " - " + str(e) + "}}xx")
            return False
        
        return True

    @staticmethod
    def create_local_students_group():
        # Make sure the group in question exists
        ret = False

        try:
            accounts.LocalGroup.create(UserAccounts.STUDENTS_GROUP)
            ret = True
        except Exception as ex:
            if ex.args[2] == "The specified local group already exists.":
                ret = True
                #print(f"Group already exists - {UserAccounts.STUDENTS_GROUP}")
                pass
            else:
                # Unexpected error
                p("}}rb" + str(ex) + "}}xx")
                ret = False
        
        # Set the description
        UserAccounts.set_group_description(UserAccounts.STUDENTS_GROUP, "OPE Students Group - Students in the group are allowed to login to this computer.")

        # if ret is True:
        #     p("}}ynOPE students group ready: " + UserAccounts.STUDENTS_GROUP + "}}xx", log_level=4)
        return ret
    
    @staticmethod
    def create_local_admins_group():
        # Make sure the group in question exists
        ret = False

        try:
            accounts.LocalGroup.create(UserAccounts.ADMINS_GROUP)
            ret = True
        except Exception as ex:
            if ex.args[2] == "The specified local group already exists.":
                ret = True
                #print(f"Group already exists - {UserAccounts.ADMINS_GROUP}")
                pass
            else:
                # Unexpected error
                p("}}rb" + str(ex) + "}}xx")
                ret = False

        # Set the description
        UserAccounts.set_group_description(UserAccounts.ADMINS_GROUP, "OPE Admins Group - Users in this group have full control over this computer.")
        
        # if ret is True:
        #     p("}}ynOPE admins group ready: " + UserAccounts.ADMINS_GROUP + "}}xx", log_level=4)
        return ret

    @staticmethod
    def disable_account(account_name=None):
        # Command that is run to start this function
        only_for = "disable_account"

        if account_name is None:
            account_name = util.get_param(2, None, only_for=only_for)
        if account_name is None:
            p("}}enInvalid User name - not disabling account!}}xx")
            return False
        try:
            user_data = dict()
            user_data['flags'] = UserAccounts.DISABLE_ACCOUNT_FLAGS
            #win32netcon.UF_SCRIPT | win32netcon.UF_ACCOUNTDISABLE
            win32net.NetUserSetInfo(None, account_name, 1008, user_data)
        except Exception as ex:
            if not "The user name could not be found." in str(ex):
                p("}}rnError - Unable to disable account: " + str(account_name) + "}}xx\n" + \
                    str(ex))
                return False
            else:
                p("}}ynLocal user not found  - skipping disable account (" + account_name + ").}}xx")
        return True
    
    @staticmethod
    def add_user_to_group(user_name, group_name):
        try:
            # Get the group
            grp = accounts.LocalGroup(accounts.group(group_name).sid)
            # Get the user
            user = accounts.user(user_name)

            grp.add(user)
        except Exception as ex:
            if ex.args[2] == "The specified account name is already a member of the group.":
                pass
            else:
                p("}}rbERROR - Unexpected exception trying to add user to group (" + \
                    user_name + "/" + group_name + "\n}}xx" + str(ex))
                return False
        return True

    @staticmethod
    def add_ad_user_to_local_group(username, domain, group_name):
        """
        Add a user to a local group on a Windows machine

        Usage:
        add_ad_user_to_local_group("user", "group")
        """
        try:

            # # Query Active Directory for user
            # pyad.pyad.BASE_DN = "DC=openelevators,DC=local"
            # q = pyad.adquery.ADQuery()
            # q.execute_query(
            #     attributes=["distinguishedName"],
            #     where_clause="sAMAccountName = '{}'".format(username),
            #     base_dn=domain
            # )

            # # Check if user exists
            # if len(list(q.get_results())) == 0:
            #     print(f"User {username} not found in Active Directory")
            #     return

            # # Get distinguished name
            # user_dn = q.get_single_result()["distinguishedName"]

            # Parse user information
            #ad_user = pyad.aduser.ADUser.from_sam_account(username)
            #ad_user = pyad.pyad.from_cn(username)

            # Get the group
            grp = accounts.LocalGroup(accounts.group(group_name).sid)
            # Get the user
            user = accounts.user(f"{domain}\\{username}")

            grp.add(user)
            print(f"ad_user: {user_dn} - {username}")

            # Get distinguished name
            #user_dn = user_dn

            # Format needed for win32net.NetLocalGroupAddMembers
            # user_info = {'domainandname': user_dn}
            
            # # Add to group
            # # win32netcon.LOCALGROUP_MEMBERS_INFO_3 - not found - value is 3
            # win32net.NetLocalGroupAddMembers(None, group_name, 3, [user_info])

            print(f"Added {UserWarning} to {group_name}")
        except Exception as ex:
            if ex.args[2] == "The specified account name is already a member of the group.":
                p("}}rbAlready A Member}}xx")
                pass
            else:
                p("}}rbERROR - Unexpected exception trying to add user to group (" + \
                    username + "/" + group_name + "\n}}xx" + str(ex))
                return False
            # print(f"Error adding {username} to {group_name} - {ex}")
            # return False

        return True


    @staticmethod
    def set_default_groups_for_admin(account_name = None):
        # Command that is run to start this function
        only_for = "set_default_groups_for_admin"

        ret = True
        # Make sure the student is in the proper groups
        if account_name is None:
            account_name = util.get_param(2, None, only_for=only_for)
        if account_name is None:
            p("}}rnInvalid User name - not adding default admin groups to account!}}xx")
            return False

        # Make sure admins group exists
        ret = UserAccounts.create_local_admins_group()

        if not UserAccounts.add_user_to_group(account_name, UserAccounts.ADMINS_GROUP):
            ret = False

        if not UserAccounts.add_user_to_group(account_name, "Administrators"):
            ret = False
        
        if not UserAccounts.add_user_to_group(account_name, "Users"):
            ret = False
        
        # # home_dir = "%s\\%s" % (server_name, user_name)
        #

        return ret

    @staticmethod
    def set_default_groups_for_student(account_name = None):
        # Command that is run to start this function
        only_for = "set_default_groups_for_student"

        ret = True
        # Make sure the student is in the proper groups
        if account_name is None:
            account_name = util.get_param(2, None, only_for=only_for)
        if account_name is None:
            p("}}rnInvalid User name - not adding default groups to user account!}}xx")
            return False

        # Make sure students group exists
        ret = UserAccounts.create_local_students_group()

        if not UserAccounts.add_user_to_group(account_name, UserAccounts.STUDENTS_GROUP):
            ret = False
        
        if not UserAccounts.add_user_to_group(account_name, "Users"):
            ret = False
        
        # # home_dir = "%s\\%s" % (server_name, user_name)
        #

        return ret

    @staticmethod
    def enable_account(account_name=None):
        # Command that is run to start this function
        only_for = "enable_account"

        if account_name is None:
            account_name = util.get_param(2, None, only_for=only_for)
        if account_name is None:
            p("}}rnInvalid User name - not enabling account!}}xx")
            return False
        
        try:
            user_data = dict()
            user_data['flags'] = UserAccounts.ENABLE_ACCOUNT_FLAGS
            #win32netcon.UF_SCRIPT | win32netcon.UF_ACCOUNTDISABLE
            win32net.NetUserSetInfo(None, account_name, 1008, user_data)
        except Exception as ex:
            p("}}rnError - Unable to enable account: " + str(account_name) + "}}xx\n" + \
                str(ex))
            return False
        
        return True

    @staticmethod
    def disable_student_accounts():
        ret = True
        # Get a list of accounts that are in the students group
        
        p("}}cb-- Disabling local student accounts in " + str(UserAccounts.STUDENTS_GROUP) + " group...}}xx")
        try:
            grp = accounts.local_group(UserAccounts.STUDENTS_GROUP)
        except winsys.exc.x_not_found as ex:
            # p("}}yn" + str(UserAccounts.STUDENTS_GROUP) + " group not found - skipping disable student accounts...}}xx")
            if ex is None:
                # shutup pylint
                pass
            return True
        
        for user in grp:
            user_name = str(user.name)
            p("}}cn-" + user_name + "}}xx")
            if not UserAccounts.disable_account(user_name):
                ret = False
        
        return ret
    
    @staticmethod
    def remove_account_profile(user_name=None):
        # Command that is run to start this function
        only_for = "remove_account_profile"

        # Remove the profile/files for the user
        if user_name is None:
            user_name = util.get_param(2, None, only_for=only_for)
        if user_name is None:
            p("}}enInvalid User name - not removing account profile!}}xx")
            return False
        
        # Log it out (if it is logged in)
        UserAccounts.log_out_user(user_name)
        
        # Get the SID for the user in question
        user_sid = ""
        try:
            parts = win32security.LookupAccountName(None, user_name)
            user_sid = win32security.ConvertSidToStringSid(parts[0])
        except Exception as ex:
            # Unable to find this user?
            p("}}rnError - Invalid User - can't remove profile!}}xx " + str(user_name))
            # shutup python
            if ex is None: pass
            return False
        
        if user_sid == "":
            # User doesn't exist?
            p("}}rnInvalid User - can't remove profile!}}xx " + str(user_name))
            return False
        
        # We need more privileges to do this next part
        UserAccounts.elevate_process_privilege_to_backup_restore()
                
        # Make sure the registry hive is unloaded
        p("Unloading " + user_sid)
        try:
            # Open/close the registry key - helps the system let go of it
            t = RegistrySettings.get_reg_value("HKEY_Users", user_sid, value_name="default", default="")

            # Unload the user hive
            r = win32api.RegUnLoadKey(win32con.HKEY_USERS, user_sid)
            p(str(r))
        except Exception as ex:
            p("}}ynUnable to unload user registry - }}xx" + str(ex), debug_level=4)

        try:
            p("Deleting profile...")
            r = win32profile.DeleteProfile(user_sid)
            p(str(r))
        except Exception as ex:
            p("}}ynUnable to remove profile folder - }}xx" + str(ex), debug_level=4)
        return True
        

        # Use WMI to delete
        # w = Computer.get_wmi_connection() # wmi.WMI()
        # # for c in w.classes:
        # #     if 'Profile' in c:
        # #         print(c)
        # profiles = w.Win32_UserProfile(SID=user_sid)
        # if profiles is None:
        #     p("Unable to find profile for user: " + str(user_sid))
        #     return False
        # for profile in profiles:
        #     #p(str(profile))
        #     if user_sid == profile.SID:
        #         p("Removing profile for: " + str(profile.LocalPath))
        #         #p(str(profile.methods.keys()))
        #         #p(str(profile.properties.keys()))
        #         p(str(profile.__dict__.keys()))
        #         p(str(profile._associated_classes))
        #         #p(str(profile.id))
        #         #p(str(profile.ole_object))
        #         wmi._wmi_method(profile.ole_object, "Delete")
        #         #profile._wmidelete()
        #         return True


        # return False

        # #See if a profile exists
        # w = wmi.WMI()
        # profiles = w.Win32_UserProfile(SID=user_sid)
        # if len(profiles) < 1:
        #     p("}}ynNo profile found for this user, skipping remove!}}xx")
        #     return True
        
        # profile_path = ""
        # profile_loaded = False
        # for profile in profiles:
        #     profile_path = profile.LocalPath
        #     profile_loaded = profile.Loaded
        # profiles = None
        # if profile_loaded is None:
        #     # shutup pylint
        #     pass
                
        # # We know it exists
        

        # # Remove it from the registry list
        # RegistrySettings.remove_key("HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\" + \
        #     "ProfileList\\" + user_sid)

        # # Delete the folder/files
        # try:
        #     shutil.rmtree(profile_path)
        # except Exception as ex:
        #     p("}}rnError - Unable to remove the profile folder at " + profile_path + "}}xx\n" + \
        #         str(ex))
        #     return False

        # return True

    @staticmethod
    def lock_screen_for_user(user_name=None):
        # Command that is run to start this function
        only_for = "lock_screen"

        # Find the user in question and lock the workstation
        if user_name is None:
            user_name = util.get_param(2, None, only_for=only_for)
        if user_name is None:
            # Lock for the current user if no name
            return UserAccounts.lock_screen_for_current_user()
        

        p("}}ybLocking screen for other users - Not Implemented Yet!}}xx")
        # TODO - lock_workstation
        # Lookup the user specified and run this under their account
        # Have rundll run the lock workstation command
        # WinApi.CreateProcessAsUser(
        #   interactiveUserToken,
        #   null,
        #   "rundll32.exe user32.dll,LockWorkStation",
        #   IntPtr.Zero,
        #   IntPtr.Zero,
        #   false,
        #   (uint)WinApi.CreateProcessFlags.CREATE_NEW_CONSOLE |
        #     (uint)WinApi.CreateProcessFlags.INHERIT_CALLER_PRIORITY,
        #   IntPtr.Zero,
        #   currentDirectory,
        #   ref siInteractive,
        #   out piInteractive);

        return False
        
    
    @staticmethod
    def lock_screen_for_current_user():
        # Locks the workstation of the current user
        return ctypes.windll.user32.LockWorkStation()
    
    @staticmethod
    def log_out_all_students_if_not_locked():
        # Allow users who are in OPEStudents or admin groups if the machine is locked down, and noone not admin if it isn't
        users = UserAccounts.get_current_login_sessions()
        is_locked = RegistrySettings.is_machine_locked()
        #p("}}cb-- Logging out all student accounts if machine is not locked...}}xx")
        for user in users:
            user_name = user[0] + "\\" + user[1]
            #p("}}cb-- Checking user: " + user_name + "}}xx")
            if UserAccounts.is_user_in_group(user_name, "OPEStudents") and is_locked == True:
                p("}}cn-" + user_name + " - allowed student and machine locked - leaving logged in.}}xx", log_level=4)
            elif UserAccounts.is_user_in_group(user_name, "OPEStudents") and is_locked == False:
                p("}}yn-" + user_name + " - allowed student and machine not locked - logging out.}}xx", log_level=2)
                UserAccounts.log_out_user(user_name)
            elif UserAccounts.is_user_in_group(user_name, "OPEAdmins") or UserAccounts.is_user_in_group(user_name, "Administrators") \
                or UserAccounts.is_user_in_group(user_name, "Dommain Admins") or UserAccounts.is_user_in_group(user_name, "OSN-Elevated"):
                p("}}cn-" + user_name + " - allowed admin - not logging out.}}xx", log_level=4)
            else:
                p("}}yn-" + user_name + " - not admin or OPEStudent - logging out.}}xx", log_level=2)
                UserAccounts.log_out_user(user_name)

        return True

    @staticmethod
    def log_out_all_students():
        # Get a list of users who are in the students group and log them out.

        students = UserAccounts.get_student_login_sessions()
        #p("}}cb-- Logging out all student accounts ...}}xx")
        for student in students:
            user_name = student[0] + "\\" + student[1]
            #p("}}cn-" + user_name + "}}xx", log_level=1)
            UserAccounts.log_out_user(user_name)

        return True

    @staticmethod
    def log_out_user(user_name=None):
        # Command that is run to start this function
        only_for = "log_out_user"

        if user_name is None:
            user_name = util.get_param(2, None, only_for=only_for)
        if user_name is None:
            p("}}rn No User name provided - not logging out!}}xx")
            return False
    
        #UserAccounts.elevate_process_privilege_to_shutdown()
        #UserAccounts.elevate_process_privilege_to_tcb()
        #UserAccounts.elevate_process_privilege_to_take_ownership()
        
        # Get list of current sessions
        sessions = win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE)  #(None, 1, 0)

        logged_off = False
        
        for session in sessions:
            active_session = session['SessionId']
            station_name = session["WinStationName"]

            #print(session)
            #print(active_session)

            # Get the user for this session
            logged_in_user_name = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE, active_session,
                win32ts.WTSUserName)
            
            if logged_in_user_name is None or logged_in_user_name == "":
                # Set this so we know it won't match later - some of the service accounts don't have a name
                logged_in_user_name = "<USERNAMEMISSING>"

            #p("}}ynComparing: " + str(user_name) + "/" + logged_in_user_name + " - " + str(active_session) + "}}xx", debug_level=3)
            # Do in comparison as doman users have the domain\user format
            if logged_in_user_name in user_name:
                # Log this one out
                p("}}gnLogging off " + str(user_name) + " - typically takes 10-120 seconds...}}xx", debug_level=4)
                try:
                    win32ts.WTSLogoffSession(win32ts.WTS_CURRENT_SERVER_HANDLE, active_session, True)
                    logged_off = True
                except Exception as ex:
                    p("}}rbError - Unable to log off user: " + str(user_name) + " - " + str(active_session) + "}}xx\n" + str(ex))
                    # Don't return false - just let it check the next session.
                

        # if logged_off is not True:
        #     p("}}ybUser not logged in - skipping log off! " + str(user_name) + "}}xx", debug_level=5)
        # else:
        #     p("}}gnUser logged out! " + str(user_name) + "}}xx", debug_level=3)

        # shutup pylint
        if station_name is None: pass

        return True

    @staticmethod
    def delete_user(user_name=None):
        # Command that is run to start this function
        only_for = "remove_account"

        if user_name is None:
            user_name = util.get_param(2, None, only_for=only_for)
        if user_name is None:
            p("}}enInvalid User name - not removing account!}}xx")
            return False
        curr_user = None
        try:
            curr_user = accounts.principal(user_name)
        except Exception as ex:
            p("}}rbInvalid User Account - Not deleting!}}xx", debug_level=1)
            return False

        # Remove the profile first
        ret = UserAccounts.remove_account_profile(user_name)
        # shutup pylint
        if ret is None: pass

        # Remove the local user
        try:
            curr_user.delete()
        except Exception as ex:
            p("}}rbError - Unable to remove account: " + str(user_name) + "}}xx\n" + str(ex))
            return False
        
        return True
    
    @staticmethod
    def disable_guest_account():
        try:
            UserAccounts.disable_account("Guest")
        except Exception as ex:
            p("}}rbERROR disabling guest account " + str(ex) + "}}xx")
            return False
        
        # Run this to disable the guest account?
        # NET USER Guest /ACTIVE:no
        return True
    
    @staticmethod
    def ensure_home_folder_for_user(curr_student):
        # NOTE - This will blow up windows profiles - win will create a new profile folder, so don't use this
        return True
        if curr_student is None or curr_student == "":
            p("}}rbMissing Username, not making profile folder}}xx")
            return False

        # Figure out path for this user
        profile_path = "c:\\users\\" + curr_student
        # Make sure this student owns and has rw access to profile folder
        if not os.path.exists(profile_path):
            p("Making profile folder for: " + str(curr_student))
            os.makedirs(profile_path, exist_ok=True)
        
        # Bump up the privileges so taking control of the folder works
        r = UserAccounts.elevate_process_privilege_to_se_security_name()

        from mgmt_FolderPermissions import FolderPermissions
        
        rights = FolderPermissions.get_acl_rights_for_user(profile_path, curr_student)
        p(str(rights))
        if 'w' not in rights:
            # Can't write to folders? reset permissions
            p("Setting permissions on home folder: " + str(curr_student) + " -> " + str(profile_path))
            r = FolderPermissions.set_home_folder_permissions(profile_path, curr_student, walk_files=False)
            if not r is True:
                p("Unable to setup profile folder, skipping lms app sync: " + str(curr_student))
                return False
        
        return True

    @staticmethod
    def ProcessLogonEvent(event_info):
        # Decide if we need to logout this user

        # event_info - user_name, domain_name, full_name, user_sid, event_type, event_time, event_source, event_id, event_data
        # SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId, TargetUserSid, TargetUserName, TargetDomainName,
        # TargetLogonId, LogonType, LogonProcessName, AuthenticationPackageName, WorkstationName,
        # LogonGuid, TransmittedServices, LmPackageName, KeyLength, ProcessId, ProcessName, IpAddress, IpPort

        # Get the user name
        user_name = event_info["user_name"]
        user_domain = event_info["domain_name"]
        user_full_name = event_info["full_name"]
        user_sid = event_info["user_sid"]
        event_type = event_info["event_type"]
        event_time = event_info["event_time"]
        event_source = event_info["event_source"]
        event_id = event_info["event_id"]
        event_data = event_info["event_data"]

        # If user is not an admin and is isn't in the OPESStudents group, log them out.
        if UserAccounts.is_user_in_group(user_name, "administrators") or UserAccounts.is_user_in_group(user_name, "OPEAdmins"):
            p("User is an admin logging in - allowing login: " + str(user_name))
            return True
        
        if UserAccounts.is_user_in_group(user_name, "OPEStudents"):
            p("User is a student logging in - allowing login: " + str(user_name))
            return True
        
        # All other instances, force the logout.
        p("User is not an admin or student or account is locked - logging out: " + str(user_name))
        return UserAccounts.log_out_user(user_name)

if __name__ == "__main__": 
    #ret = UserAccounts.create_local_students_group()
    #ret = UserAccounts.create_local_student_account("s999999", "Test Student", "Sid999999!")
    #print("RET: " + str(ret))
    #print("Log out all students...")
    #print(UserAccounts.get_active_user_name())
    #UserAccounts.log_out_all_students()
    ret = UserAccounts.create_local_students_group()
    print("RET: " + str(ret))
    #UserAccounts.add_ad_user_to_local_group("s777777", "osn.local", "OPEStudents")
    #UserAccounts.add_user_to_group("osn.local\\s777777", "OPEStudents")
    UserAccounts.disable_account("s777778")