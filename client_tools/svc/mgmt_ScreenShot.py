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
from mgmt_EventLog import EventLog

global LOGGER
LOGGER = EventLog.get_current_instance()


class ScreenShot:
    # Class to deal with grabbing screen shots
    
    # Disable sshot if this is set
    DISABLE_SSHOT = False

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

    _LOG_INSTANCE = None

    @staticmethod
    def log_event(msg, is_error=False, show_in_event_log=True, log_level=3):

        if ScreenShot._LOG_INSTANCE is None:
            ScreenShot._LOG_INSTANCE = EventLog.get_current_instance()
        
        if not ScreenShot._LOG_INSTANCE is None:
            ScreenShot._LOG_INSTANCE.log_event(msg, is_error, show_in_event_log, log_level)

        return
    
    @staticmethod
    def init_globals():
        if os.path.isfile(os.path.join(util.ROOT_FOLDER, ".disable_sshot")):
            ScreenShot.log_event("}}rb**** WARNING **** screen shots disabled!}}xx", log_level=2)
            ScreenShot.DISABLE_SSHOT = True
    pass

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
        active_session = ScreenShot.WTS_INVALID_SESSION_ID
        station_name = ""
        sessions = win32ts.WTSEnumerateSessions(None, 1, 0)
        
        for session in sessions:
            if session['State'] == ScreenShot.WTSActive:
                # Found the active session
                active_session = session['SessionId']
                station_name = session["WinStationName"]

        # If we didn't find one, try this way
        if active_session == ScreenShot.WTS_INVALID_SESSION_ID:
            active_session = win32ts.WTSGetActiveConsoleSessionId()
        if active_session == ScreenShot.WTS_INVALID_SESSION_ID:
                # User not logged in right now? or lock screen up?
                ScreenShot.log_event("}}gnNo console user or desktop locked}}xx", log_level=1)
                return ret
            
        # Get the current console session
        ScreenShot.log_event("Got Console: " + str(active_session), log_level=4)

        # Login to the terminal service to get the user token for the console id so we can impersonate it
        try:
            #svr = win32ts.WTSOpenServer(".")
            #user_token = win32ts.WTSQueryUserToken(active_session)
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
            ScreenShot.log_event("}}rnUnknown Error - trying to get WTS UserToken\n" + str(ex) + "}}xx", log_level=1)
            return ret
        
        ScreenShot.log_event("User Token Found " + str(user_token_copy), log_level=5)

        return ret

    @staticmethod
    def take_screenshot():
        ret = False
        ScreenShot.init_globals()

        if ScreenShot.DISABLE_SSHOT:
            ScreenShot.log_event("}}ybSkipping screen shot - disabled by .disable_sshot file}}xx", log_level=2)
            return
        
        # Find the logged in user and run the sshot.exe app
        cmd = os.path.join(util.BINARIES_FOLDER, "sshot\\sshot.exe")
        
        ScreenShot.log_event("}}gnTrying to run " + cmd + "}}xx", log_level=4)

        user_token = ScreenShot.get_active_user_token()
        if user_token is None:
            ScreenShot.log_event("}}ynUnable to get user token - screen locked?}}xx", log_level=2)
            return ret

        sidObj, intVal = win32security.GetTokenInformation(user_token, win32security.TokenUser)
        #source = win32security.GetTokenInformation(tokenh, TokenSource)
        if sidObj:
            accountName, domainName, accountTypeInt = win32security.LookupAccountSid(".", sidObj)
            ScreenShot.log_event("}}gnRunning As: " + accountName + "}}xx", log_level=2)
        else:
            ScreenShot.log_event("}}rnUnable to get User Token! }}xx", log_level=1)
            return None
        ScreenShot.log_event("}}gnFound User Token: " + str(user_token) + "}}xx", log_level=5)

        # Put this token in the logged in session
        #win32security.SetTokenInformation(user_token_copy, win32security.TokenSessionId, session_id)

        # Use win create process function
        si = win32process.STARTUPINFO()
        si.dwFlags = win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_NORMAL
        # si.lpDesktop = "WinSta0\Default"
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

            ScreenShot.log_event("Process Started: " + str(dwProcessId), log_level=5)
            ScreenShot.log_event(hProcess, log_level=5)
            ret = True
        except Exception as e:
            ScreenShot.log_event("}}rnError launching process:}}xx\n" + str(e), log_level=1)
            
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
            ScreenShot.log_event("}}gnSnapped.}}xx", log_level=3)
        
        return ret
        

# Switch to the user
# NOTE - Impersionation not working? Run process ass
# win32security.ImpersonateLoggedOnUser(user_token)
# logging.info("Impersonating " + win32api.GetUserName())
# Return us to normal security
# win32security.RevertToSelf()
