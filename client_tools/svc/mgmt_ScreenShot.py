# Needed for running as alternate user
import win32ts
import win32security
import win32con
import win32process
import win32api
import win32profile

import subprocess
import sys
import os

from color import p

import util
from mgmt_UserAccounts import UserAccounts
from mgmt_ProcessManagement import ProcessManagement

class ScreenShot:
    # Class to deal with grabbing screen shots
    
    # Disable sshot if this is set
    DISABLE_SSHOT = False

    @staticmethod
    def init_globals():
        if os.path.isfile(os.path.join(util.ROOT_FOLDER, ".disable_sshot")):
            p("}}rb**** WARNING **** screen shots disabled!}}xx", log_level=2)
            ScreenShot.DISABLE_SSHOT = True
    pass

    @staticmethod
    def take_screenshot():
        ret = False
        ScreenShot.init_globals()

        if ScreenShot.DISABLE_SSHOT:
            p("}}ybSkipping screen shot - disabled by .disable_sshot file}}xx", log_level=2)
            return
        
        # Find the logged in user and run the sshot.exe app
        cmd = os.path.join(util.BINARIES_FOLDER, "sshot\\sshot.exe")
        
        p("}}gnTrying to run " + cmd + "}}xx", log_level=4)

        user_token = UserAccounts.get_active_user_token()
        if user_token is None:
            p("}}ynUnable to get user token - screen locked?}}xx", log_level=2)
            return ret

        sidObj, intVal = win32security.GetTokenInformation(user_token, win32security.TokenUser)
        #source = win32security.GetTokenInformation(tokenh, TokenSource)
        if sidObj:
            accountName, domainName, accountTypeInt = \
                win32security.LookupAccountSid(".", sidObj)
        else:
            p("}}rnUnable to get User Token! }}xx", log_level=1)
            return None
        #p("}}gnFound User Token: " + str(user_token) + "}}xx", log_level=5)

        # If user is in the administrators group, skip taking the sshot
        if UserAccounts.is_in_admin_group(accountName):
            p("}}mbUser (" + accountName + ") is in admin group, skipping screen shot...}}xx")
            return True

        p("}}gnRunning As: " + accountName + "}}xx", log_level=2)
        # Put this token in the logged in session
        #win32security.SetTokenInformation(user_token_copy, win32security.TokenSessionId, session_id)

        # Use win create process function
        si = win32process.STARTUPINFO()
        si.dwFlags = win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_NORMAL
        # si.lpDesktop = "WinSta0\Default"   ## For secure desktop, "WinSta0\\Winlogon"
        si.lpDesktop = "WinSta0\\Default"

        # Setup envinroment for the user
        environment = win32profile.CreateEnvironmentBlock(user_token, False)

        try:
            (hProcess, hThread, dwProcessId, dwThreadId) = win32process.CreateProcessAsUser(user_token,
                                            None,   # AppName (really command line, blank if cmd line supplied)
                                            "\"" + cmd + "\"",  # Command Line (blank if app supplied)
                                            None,  # Process Attributes
                                            None,  # Thread Attributes
                                            0,  # Inherits Handles
                                            win32con.NORMAL_PRIORITY_CLASS,  # or win32con.CREATE_NEW_CONSOLE,
                                            environment,  # Environment
                                            os.path.dirname(cmd),  # Curr directory
                                            si)  # Startup info

            p("Process Started: " + str(dwProcessId), log_level=5)
            p(hProcess, log_level=5)
            ret = True
        except Exception as e:
            p("}}rnError launching process:}}xx\n" + str(e), log_level=1)
            
        # Cleanup
        user_token.close()

        # else:
        #     # Not logged in as system user, run as current user
        #     try:
        #         timeout = 10 # 10 seconds?
        #         # Log an error if the process doesn't return 0
        #         # stdout=PIPE and stderr=STDOUT instead of capture_output=True
        #         p("}}gnRunning as current user " + user_name + "}}xx")
        #         proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,timeout=timeout, check=False)
        #         if (proc.returncode == 0):
        #             p("Command Results: " +  cmd + "\n" + proc.stdout.decode())
        #             ret = True
        #         else:
        #             p("*** Command Failed!: " + cmd + "(" + str(proc.returncode) + ") \n" + proc.stdout.decode())
        #     except Exception as ex:
        #         p("*** Command Exception! " + cmd + " \n" + \
        #             str(ex))
            
        if ret is True:
            p("}}gnSnapped.}}xx", log_level=3)
        
        return ret
        

# Switch to the user
# NOTE - Impersionation not working? Run process ass
# win32security.ImpersonateLoggedOnUser(user_token)
# logging.info("Impersonating " + win32api.GetUserName())
# Return us to normal security
# win32security.RevertToSelf()
