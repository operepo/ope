# Needed for external stuff?
#import pythoncom

## Service Imports
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

import win32evtlog
import win32ts

import win32timezone

import win32traceutil
import traceback
import threading

# Needed for device events
import win32gui
import win32gui_struct
import win32con

import time
import random
import subprocess
import sys
import os
import random

from collections import OrderedDict

import util

import mgmt_UserAccounts

# Pull in logger first and set it up!
from mgmt_EventLog import EventLog
global LOGGER
LOGGER = EventLog(os.path.join(util.LOG_FOLDER, 'ope-service.log'), service_name="OPEService")

from color import p, set_log_level, get_log_level

# Import local modules
from mgmt_RegistrySettings import RegistrySettings


class OPEService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'OPEService'
    _svc_display_name_ = 'OPEService'
    _svc_description_ = "Open Prison Education Service"

    _svc_instance = None

    _WAIT_TIMEOUT_MSEC = 250

    # Prevent device event storm (device event that causes another device event)
    # When needed, don't fire the event for ?? seconds
    # any new events reset the timer
    _DEVICE_EVENT_NEEDED = False
    _LAST_DEVICE_EVENT = 0
    _LAST_DEVICE_EVENT_PARAMS = ()
    # Delay before firing device event (e.g. don't scan_nics for a few seconds)
    _DEVICE_EVENT_DELAY = 10
    

    # GUID to subscribe to - we wan't USB events
    GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
    
    # Track last time the command was run
    _COMMAND_NEXT_RUN_TIMES = {}

    # Queue of commands
    _COMMAND_QUEUE = OrderedDict()
    # Thread that grabs and runs commands (created in __init__)
    _COMMAND_QUEUE_THREAD = None

    # Thread that monitors login events from windows
    _MONITOR_LOGIN_THREAD = None

    # Threads that are currently running
    #_RUNNING_COMMAND_THREADS = {}

    @staticmethod
    def check_device_event_queue():
        # Check if a device event has happend and if it is time to run the 
        # mgmt command device_events (avoid event storm and double bounce)

        # First - exit if there haven't been any events since the last time this
        # was fired
        if OPEService._DEVICE_EVENT_NEEDED is not True:
            # Not needed, lets leave
            p("Device event not queued, skipping", log_level=5)
            return True

        # We might get MANY of these events, basically don't run it until it has been < ??
        # seconds since the last device event
        if time.time() - OPEService._LAST_DEVICE_EVENT > OPEService._DEVICE_EVENT_DELAY:
            p("Device event needed - appropriate time has passed since last event", log_level=4)
            # Time to actually run the device_event/scan_nics
            OPEService._svc_instance.run_command("device_event", OPEService._LAST_DEVICE_EVENT_PARAMS, force_run=True)
            OPEService._DEVICE_EVENT_NEEDED = False
            return True
        
        p("Device event needed, but not time to run", log_level=5)
        return False
                

    @staticmethod
    def reload_settings():
        p("}}ybRunning reload_settings}}xx")
        # Reload settings for the service from the registry
        if OPEService._svc_instance is None:
            p("}}rbNo OPEService running? - NOT reloading settings!")
            return False
        
        p("}}mbReloading Settings}}xx", log_level=4)

        #### Grab settings from the registry

        if LOGGER is not None:
            # Grab log level
            value_name = "log_level"
            value = RegistrySettings.get_reg_value(app="OPEService",
                value_name=value_name, default=3, value_type="REG_DWORD")
            # Set log_level through color/p - it passes things on to the logger
            old_val = get_log_level()
            set_log_level(value)
            if old_val != value:
                p("}}ybNew Setting " + value_name + \
                    ": " + str(value) + "}}xx", log_level=3)
            

        # Grab how often to run default permissions (registry and ope folder)
        value_name = "set_default_permissions_timer"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default=3600, value_type="REG_DWORD")
        old_val = OPEService._COMMANDS_TO_RUN["set_default_ope_folder_permissions"]["timer"]
        if old_val != value:
            p("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=3)
        OPEService._COMMANDS_TO_RUN["set_default_ope_folder_permissions"]["timer"] = value
        OPEService._COMMANDS_TO_RUN["set_default_ope_registry_permissions"]["timer"] = value


        # How often should we run reload_settings function?
        value_name = "reload_settings_timer"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default=30, value_type="REG_DWORD")
        old_val = OPEService._COMMANDS_TO_RUN["reload_settings"]["timer"]
        if old_val != value:
            p("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=3)
        OPEService._COMMANDS_TO_RUN["reload_settings"]["timer"] = value

        # How often should we run scan_nics
        value_name = "scan_nics_timer"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default=60, value_type="REG_DWORD")
        old_val = OPEService._COMMANDS_TO_RUN["scan_nics"]["timer"]
        if old_val != value:
            p("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=3)
        OPEService._COMMANDS_TO_RUN["scan_nics"]["timer"] = value


        # How often should we run screen_shot
        value_name = "screen_shot_timer"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default="30-300", value_type="REG_SZ")
        old_val = OPEService._COMMANDS_TO_RUN["screen_shot"]["timer"]
        if old_val != value:
            p("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=3)
        OPEService._COMMANDS_TO_RUN["screen_shot"]["timer"] = value

        return True

    # Command + time to run it
    # -1 - Don't run at all unless called w force_run (no timer)
    # 0 - Run once, then stop (startup only)
    # int - when to run next (in seconds - curr_time + this)
    # "1-10" - String - range for random time to run
    #
    # For cmd = %mgmt% will be translated to the path to the mgmt utility
    # same with %sshot% (sshot shouldn't be needed anymore - run it all through mgmt)
    _COMMANDS_TO_RUN = {
        "set_default_ope_folder_permissions": {
            "cmd": "%mgmt% set_default_ope_folder_permissions",
            "timer": 3*3600
        },
        "set_default_ope_registry_permissions": {
            "cmd": "%mgmt% set_default_ope_registry_permissions",
            "timer": 3*3600
        },
        "reload_settings": {
            # use.__func__ to access static methods function while defining
            "cmd": reload_settings.__func__,
            "timer": 30
        },
        "scan_nics": {
            "cmd": "%mgmt% scan_nics",
            "timer": 1200
        },
        "screen_shot": {
            "cmd": "%mgmt% screen_shot",
            "timer": "30-300"
            #"timer": "60-600"   # 1 - 10 minutes
        },

        # Check if a device event has happend and if it is time to run the 
        # mgmt command device_events (avoid event storm and double bounce)
        "check_device_event_queue": {
            "cmd": check_device_event_queue.__func__,
            "timer": 30     # run often - we will filter out extras in the function
        },

        # Run the actual device event (e.g. mgmt.exe device_event)
        "device_event": {
            "cmd": "%mgmt% device_event",
            "timer": -1  # Don't run normally - only when fired from device event            
        },
        "ping_smc": {
            "cmd": "%mgmt% ping_smc",
            "timer": 15 # See if we can hit the smc server
        },
        "log_out_all_students_if_not_locked": {
            "cmd": "%mgmt% log_out_all_students_if_not_locked",
            "timer": 30
        }
        
    }

    def get_next_command_run_time(self, command_name):
        # Get the timer
        timer = 0
        if command_name in OPEService._COMMANDS_TO_RUN:
            try:
                timer = int(OPEService._COMMANDS_TO_RUN[command_name]["timer"])
            except:
                timer = 0
        else:
            # invalid command?
            timer = -1

        if timer == -1:
            # Disable this one
            OPEService._COMMAND_NEXT_RUN_TIMES[command_name] = timer
            return timer
        
        if timer == 0 and command_name not in OPEService._COMMAND_NEXT_RUN_TIMES:
            # Haven't run this yet - run it once
            next_run_time = time.time()-1
            return next_run_time
        
        # Default to need to run (1 second ago) - any command that hasn't started yet
        # needs to
        next_run_time = time.time()-1
        
        if command_name in OPEService._COMMAND_NEXT_RUN_TIMES:
            next_run_time = OPEService._COMMAND_NEXT_RUN_TIMES[command_name]
        
        #p(command_name + " - Next run time: " + str(next_run_time), log_level=4)
        return next_run_time
    
    def reset_next_command_run_time(self, command_name):
        # Calculate the time for running this command again
        if command_name in OPEService._COMMANDS_TO_RUN:
            timer = OPEService._COMMANDS_TO_RUN[command_name]["timer"]
            
            # if timer is a string (e.g. 1-10) then split it and make a new random value
            # in that range
            if isinstance(timer, str):
                parts = timer.split("-")
                if len(parts) == 2:
                    try:
                        start_int = int(parts[0])
                        end_int = int(parts[1])
                        timer = random.randint(start_int, end_int)
                        p("Found random range - new timer = +" + str(timer) + \
                            " seconds", log_level=4)
                    except:
                        p("Invalid timer format defaulting to 60 seconds? " + \
                            str(timer) + " / " + command_name, log_level=2)
                        timer = 60
            
                else:
                    # String value, try just converting to int
                    try:
                        timer = int(timer)
                    except:
                        # invalid format??
                        p("Invalid timer format defaulting to 60 seconds? " + \
                            str(timer) + " / " + command_name, log_level=2)
                        timer = 60
            
            # Calculate next run time
            if timer > 0:
                next_run_time = time.time() + timer
                OPEService._COMMAND_NEXT_RUN_TIMES[command_name] = next_run_time
                p("Next run time " + command_name + " (" + str(timer) + \
                    " seconds)", log_level=3)
            else:
                # Timer = 0 - set next run to -1 (disabled)
                OPEService._COMMAND_NEXT_RUN_TIMES[command_name] = -1
                p("Timer < 1 - skipping re-schedule " + command_name, log_level=4)
        else:
            # Shouldn't be scheduling a command that doesn't exist?
            p("Trying to schedule a bad command to run? " + command_name, log_level=1)

    def monitor_login_events_thread(self):
        server = 'localhost'  # Can be 'localhost' or the name of a remote computer
        logtype = 'Security'
        event_id = 4624  # Event ID for successful login

        # Open a handle to the Security event log
        handle = win32evtlog.OpenEventLog(server, logtype)
        #p(f"Thread Handle: {handle}", log_level=3)
        # Make sure to flush logs to the win event log system
        #LOGGER.flush_win_logs()
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        p("Monitor login thread running....", log_level=3)
        while self.isAlive is True:
            try:
                events = win32evtlog.ReadEventLog(handle, flags, 0)
                for event in events:
                    #p(f"got login event...{event}", log_level=3)

                    event_info = {}
                    event_info["TimeGenerated"] = event.TimeGenerated
                    event_info["SourceName"] = event.SourceName
                    event_info["EventID"] = event.EventID
                    event_info["EventType"] = event.EventType
                    event_info["RecordNumber"] = event.RecordNumber
                    event_info["Sid"] = event.Sid
                    event_info["StringInserts"] = event.StringInserts
                    event_info["Category"] = event.EventCategory
                    event_info["ComputerName"] = event.ComputerName
                    event_info["Data"] = event.Data
                    event_info["EventID"] = event.EventID
                    event_info["EventCategory"] = event.EventCategory
                    event_info["LogonType"] = "2"

                    string_inserts = event.StringInserts


                    if len(string_inserts) >= 20:
                        # If LogonType == 5 - it is a service logon - ignore it
                        # 2 - interactive, 7 - unlock, 10 - remote, 11 - cachedinteractive
                        # LogonType 2: Interactive (A user logged on to this computer locally)
                        # LogonType 3: Network (A user or computer logged on to this computer from the network)
                        # LogonType 4: Batch (Batch logon type is used by batch servers, where processes may be executing on behalf of a user without their direct intervention)
                        # LogonType 5: Service (A service was started by the Service Control Manager)
                        # LogonType 7: Unlock (This workstation was unlocked)
                        # LogonType 8: NetworkCleartext (A user logged on to this computer from the network using a cleartext password)
                        # LogonType 9: NewCredentials (A caller has cloned its current token and specified new credentials for outbound connections)
                        # LogonType 10: RemoteInteractive (A user logged on to this computer remotely using Terminal Services or Remote Desktop)
                        # LogonType 11: CachedInteractive (A user logged on to this computer with network credentials that were stored locally on the computer)
                        #p(f"SubjectUserSid: {string_inserts[0]}")
                        event_info["SubjectUserSid"] = string_inserts[0]
                        #p(f"SubjectUserName: {string_inserts[1]}")
                        event_info["SubjectUserName"] = string_inserts[1]
                        #p(f"SubjectDomainName: {string_inserts[2]}")
                        event_info["SubjectDomainName"] = string_inserts[2]
                        #p(f"SubjectLogonId: {string_inserts[3]}")
                        event_info["SubjectLogonId"] = string_inserts[3]
                        #p(f"TargetUserSid: {string_inserts[4]}")
                        event_info["TargetUserSid"] = string_inserts[4]
                        #p(f"TargetUserName: {string_inserts[5]}")
                        event_info["TargetUserName"] = string_inserts[5]
                        #p(f"TargetDomainName: {string_inserts[6]}")
                        event_info["TargetDomainName"] = string_inserts[6]
                        #p(f"TargetLogonId: {string_inserts[7]}")
                        event_info["TargetLogonId"] = string_inserts[7]
                        #p(f"LogonType: {string_inserts[8]}")
                        event_info["LogonType"] = string_inserts[8]
                        #p(f"LogonProcessName: {string_inserts[9]}")
                        event_info["LogonProcessName"] = string_inserts[9]
                        #p(f"AuthenticationPackageName: {string_inserts[10]}")
                        event_info["AuthenticationPackageName"] = string_inserts[10]
                        #p(f"WorkstationName: {string_inserts[11]}")
                        event_info["WorkstationName"] = string_inserts[11]
                        #p(f"LogonGuid: {string_inserts[12]}")
                        event_info["LogonGuid"] = string_inserts[12]
                        #p(f"TransmittedServices: {string_inserts[13]}")
                        event_info["TransmittedServices"] = string_inserts[13]
                        #p(f"LmPackageName: {string_inserts[14]}")
                        event_info["LmPackageName"] = string_inserts[14]
                        #p(f"KeyLength: {string_inserts[15]}")
                        event_info["KeyLength"] = string_inserts[15]
                        #p(f"ProcessId: {string_inserts[16]}")
                        event_info["ProcessId"] = string_inserts[16]
                        #p(f"ProcessName: {string_inserts[17]}")
                        event_info["ProcessName"] = string_inserts[17]
                        #p(f"IpAddress: {string_inserts[18]}")
                        event_info["IpAddress"] = string_inserts[18]
                        #p(f"IpPort: {string_inserts[19]}")
                        event_info["IpPort"] = string_inserts[19]
                    else:
                        p(f"Event does not contain all expected fields. \n{string_inserts}", log_level=3)
                        continue

                    if event.EventID == event_id and (event_info["LogonType"] != "5"):
                        p(f"*** Interactive Login event detected.\n{event_info}", log_level=3)
                        mgmt_UserAccounts.ProcessLogonEvent(event_info)
                        # if username.lower() in [s.lower() for s in event.StringInserts if s]:
                        #     print(f"Login attempt detected for user: {username}")
                        #     disable_user_account(username)
                        #     return
                        #print(f"Event Category: {event.EventCategory}")
                        # print(f"Time Generated: {event.TimeGenerated}")
                        # print(f"Source Name: {event.SourceName}")
                        # print(f"Event ID: {event.EventID}")
                        # print(f"Event Type: {event.EventType}")
                        # print(f"Event Record: {event.RecordNumber}")
                        # print(f"User SID: {event.Sid}")
                        # print(f"Event Data: {event.StringInserts}")
                        # print("="*50)
                        #
                        
            except Exception as e:
                p("}}rbAn error occurred trying to check for login events: " + f"{e}" + "}}xx")
        
            # Slight pause to slow the loop down
            time.sleep(0.5)

        if not handle is None:
            p("Closing event log handle...", log_level=3)
            win32evtlog.CloseEventLog(handle)
            handle = None
        p("Monitor login thread exiting...", log_level=3)
        return True

    def command_queue_thread(self):
        # Pick commands off the queue and run them.
        p("Command queue thread running...", log_level=3)
        while self.isAlive is True:
            try:
                # See if we are paused during an update.
                last_update_time = RegistrySettings.get_reg_value(
                    value_name="upgrade_started",
                    default=-1
                )
                curr_time = time.time()
                max_upgrade_time = 10*60  # 10 mins
                paused = False
                if last_update_time == -1:
                    # Not paused.
                    paused = False
                elif curr_time - last_update_time > max_upgrade_time:
                    # Upgrade taking too long?
                    p("CQT-Upgrade taking too long, resuming commands.", log_level=3)
                    paused = False
                    # Reset the registry key
                    RegistrySettings.set_reg_value(value_name="upgrade_started", value=-1)
                elif curr_time - last_update_time < max_upgrade_time:
                    paused = True
                    # Waiting for update to finish, skip commands
                    if RegistrySettings.is_timer_expired(timer_name="service_paused_timer", time_span=120):
                        p("CQT-Paused waiting for upgrade to finish...", log_level=3)

                # Grab the next command
                if not paused is True and len(OPEService._COMMAND_QUEUE) > 0:
                    # Get the command from the queue and remove it
                    key, cmd_obj = OPEService._COMMAND_QUEUE.popitem(last=False)
                    command_name = cmd_obj['command_name']
                    command_args = cmd_obj['args']
                    p("Command queue thread popped command: " + str(command_name), log_level=5)

                    # Reset timer so it doesn't run again for a bit
                    self.reset_next_command_run_time(command_name)

                    # Execute this command
                    self.execute_command(
                        command_name=command_name,
                        args=command_args)
                
            except Exception as ex:
                p("}}rbUnknown Exception! command_queue_thread " + \
                    "}}xx\n" + str(ex) + "\n" + \
                    traceback.format_exc(), log_level=1)
                            
            # Slight pause to slow the loop down
            time.sleep(0.5)

        p("Command queue thread exiting...", log_level=3)
        return True
    
    def run_command(self, command_name, args=None, force_run=False):

        # Run the command - if force_run isn't True, it will not run
        # the command if it isn't time yet (it will ignore the call)
        time_to_run = False
        # p("Run command called: " + command_name)

        try:
            # See if it is time to run
            next_run_time = self.get_next_command_run_time(command_name)
            # Time left will be how many seconds to wait - anything = or negative means we are that far past time
            time_left = next_run_time - time.time()
            if next_run_time < 1:
                # Don't run commands w a 0 or -1 unless they have force_run on
                pass
            elif time_left <= 0:
                # Need to run command
                time_to_run = True

            if force_run is True:
                time_to_run = True
            
            if time_to_run is True:
                # Time to run the command - make sure it isn't queued already.        
                if command_name in OPEService._COMMAND_QUEUE:
                    p("Command already queued, skipping", log_level=6)
                    # Re-queue the command if needed
                    self.reset_next_command_run_time(command_name)
                    return True
                
                # Add command to queue so it will run later.
                cmd_obj = dict(command_name=command_name, args=args)
                OPEService._COMMAND_QUEUE[command_name] = cmd_obj
                
            else:
                # Note - This will generate a LOT of entries - need to collapse/limit this?
                p("Not time to run command, ignoring: " + command_name + \
                    " (" + str(time_left) + " seconds left)",
                    log_level=6)
                pass
        except Exception as ex:
            p("}}rbUnknown Exception! Trying to run command " + \
                command_name + "}}xx\n" + str(ex), log_level=1)
    
    def execute_command(self, command_name, args=None):
        # Run the actual command in a different thread so it doesn't
        # block the main app
        
        cmd = OPEService._COMMANDS_TO_RUN[command_name]["cmd"]
        cmd_start = time.time()

         # Is this a function pointer or a command line string?
        if callable(cmd):
            # Function pointer
            p("}}mbRunning command (function): " + command_name +
                " - (" + str(cmd) + " Args: " + str(args) + ")}}xx",
                log_level=3)
            try:
                r = cmd()
            except Exception as ex:
                p("}}rb*** ERROR RUNNING FUNCTION ***}}xx\n" + str(ex))
                
        else:
            # Command string
            # Replace %sshot% and %mgmt% w valid path
            cmd = self.fix_path_variables(cmd)

            p("}}mbRunning command: " + command_name + \
                " - (" + str(cmd) + " Args: " + str(args) + ")}}xx",
                log_level=3)

            # Run the command
            timeout = 10*60 # 10 mins?
            try:
                # Log an error if the process doesn't return 0
                # stdout=PIPE and stderr=STDOUT instead of capture_output=True
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=timeout,
                    check=False
                )
                if (proc.returncode == 0):
                    p("}}mnCommand Results: " + command_name + " - Args: " +
                        str(args) + "}}xx\n" + proc.stdout.decode(), log_level=3)
                else:
                    p("}}rn*** Command Failed!: " + command_name +
                        "(Return: " + str(proc.returncode) + ") - " + str(args) +
                        " --- }}xx\n" + proc.stdout.decode(), log_level=2)
            except Exception as ex:
                p("}}rb*** Command Exception! " + command_name + \
                    " - " + str(args) + " --- }}xx\n" + \
                    str(ex), log_level=1)
        
        cmd_end = time.time()
        p("Command execution time: " + command_name + " " + str(cmd_start) + "/" + str(cmd_end) + " took " + str(cmd_end - cmd_start) + " seconds", log_level=5)

        # Make sure to flush logs to the win event log system
        LOGGER.flush_win_logs()

        # Have thread remove itself from the list
        #self.running_command_threads.remove(threading.current_thread())
        # p("Command Finished: " + command_name + " - " + str(args))
        return True
        
    
    def fix_path_variables(self, cmd):
        #p("util.BINARIES_FOLDER: " + util.BINARIES_FOLDER)

        # Replace variables such as %sshot% and %mgmt% w proper path
        mgmt_path = os.path.normpath(os.path.join(util.BINARIES_FOLDER, "mgmt/mgmt.exe"))
        sshot_path = os.path.normpath(os.path.join(util.BINARIES_FOLDER, "sshot/sshot.exe"))
        
        cmd = cmd.replace("%mgmt%", mgmt_path)
        cmd = cmd.replace("%sshot%", sshot_path)

        p("fix_path_variable: " + cmd, log_level=5)

        return cmd
        
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        if OPEService._svc_instance is not None:
            p("}}rbAnother instance of OPEService decteced?!?!? FIX}}xx")
        OPEService._svc_instance = self

        # Make sure our command queue thread is running.
        if OPEService._COMMAND_QUEUE_THREAD is None:
            t = threading.Thread(target=self.command_queue_thread,
                daemon=True,  # Make sure thread ends when service stops
                name="OPECommandQueueThread"
                )
            t.start()
        
        # Make sure our thread to monitor logins is running
        if OPEService._MONITOR_LOGIN_THREAD is None:
            t = threading.Thread(target=self.monitor_login_events_thread,
                daemon=True,  # Make sure thread ends when service stops
                name="MonitorLoginThread"
                )
            t.start()

        try:
            # The signal that "stop" has been hit on the service
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            
            # Why set socket timeout? Not sure - in all the examples
            socket.setdefaulttimeout(60)
            self.isAlive = True
           
        except Exception as ex:
            p("}}rnUnknonw Exception: }}xx\n" + str(ex))

    # Override the base class so we can accept additional device events.
    def GetAcceptedControls(self):
        # say we accept them all.
        rc = win32serviceutil.ServiceFramework.GetAcceptedControls(self)
        rc |= win32service.SERVICE_ACCEPT_PARAMCHANGE \
              | win32service.SERVICE_ACCEPT_NETBINDCHANGE \
              | win32service.SERVICE_CONTROL_DEVICEEVENT \
              | win32service.SERVICE_ACCEPT_HARDWAREPROFILECHANGE \
              | win32service.SERVICE_ACCEPT_POWEREVENT \
              | win32service.SERVICE_ACCEPT_SESSIONCHANGE
        return rc
    
    def ListenForDeviceEvents(self):

        try:
            # register for a device notification - we pass our service handle
            # instead of a window handle.
            filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
                                            OPEService.GUID_DEVINTERFACE_USB_DEVICE)
            self.hdn = win32gui.RegisterDeviceNotification(self.ssh, filter,
                                        win32con.DEVICE_NOTIFY_SERVICE_HANDLE)
            
            p("}}cnService now listening for device events", log_level=3)
        except Exception as ex:
            p("Unknown Error listening for device events " + str(ex), log_level=1)
        
        return

    # All extra events are sent via SvcOtherEx (SvcOther remains as a
    # function taking only the first args for backwards compat)
    def SvcOtherEx(self, control, event_type, data):
        # This is only showing a few of the extra events - see the MSDN
        # docs for "HandlerEx callback" for more info.
        if control == win32service.SERVICE_CONTROL_DEVICEEVENT:
            info = win32gui_struct.UnpackDEV_BROADCAST(data)
            msg = "A device event occurred (queued up running scan_nics): %x - %s" % (event_type, info)
            OPEService._LAST_DEVICE_EVENT = time.time()
            OPEService._LAST_DEVICE_EVENT_PARAMS = (event_type, info)
            OPEService._DEVICE_EVENT_NEEDED = True
            # command will run when it is time
            p("-- Device Event Happended - queued device_event command for later " + msg, log_level=2)
            return

        elif control == win32service.SERVICE_CONTROL_HARDWAREPROFILECHANGE:
            msg = "A hardware profile changed: type=%s, data=%s" % (event_type, data)
        elif control == win32service.SERVICE_CONTROL_POWEREVENT:
            msg = "A power event: setting %s" % data
            self.run_command("device_event", (event_type, info), force_run=True)
        elif control == win32service.SERVICE_CONTROL_SESSIONCHANGE:
            # data is a single elt tuple, but this could potentially grow
            # in the future if the win32 struct does
            msg = "Session event: type=%s, data=%s" % (event_type, data)
            if event_type == win32ts.WTS_SESSION_LOGON:
                # Logon event
                p(f"SvcOtherEx - Login event detected - {data}", log_level=3)
            elif event_type == win32ts.WTS_SESSION_LOGOFF:
                # Logoff event
                p(f"SvcOtherEx - Logoff event detected - {data}", log_level=3)
                
        else:
            msg = "Other event: code=%d, type=%s, data=%s" \
                  % (control, event_type, data)

        p("-- SvcOtherEx - Other Event " + msg, log_level=2)
        

    def SvcStop(self):
        try:
            self.isAlive = False

            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

            win32event.SetEvent(self.hWaitStop)
            p("}}cnService Stop Event Recieved, Stopping Service", log_level=1)
        except Exception as ex:
            p("}}rbUnknown Exception: }}xx\n" + str(ex), log_level=1)
        
    def SvcDoRun(self):
        self.isAlive = True

        # Make sure we are listening for device insert events
        self.ListenForDeviceEvents()

        # Generic exception catch to protect app
        try:

            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            p("}}cb***** OPEService running *****}}xx", log_level=1)

            # Do we need a seprate event entry for this?
            try:
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                                servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
            except Exception as ex:
                p("}}ybUnable to log message:}}xx " + str(ex))

            self.main()
            # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

            # Write a stop message.
            p("}}cb***** OPEService Stopping *****}}xx", log_level=1)
            # Do we need a seperate event entry for this?
            try:
                servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STOPPED,
                    (self._svc_name_, '')
                    )
            except Exception as ex:
                p("}}ybUnable to log message:}}xx " + str(ex))
            
        except Exception as ex:
            p("}}rbUnknown Exception: }}xx\n" + str(ex), log_level=1)
            pass
        
        # try:
        #     p("}}cn***** Cleaning up worker threads: " + \
        #         str(len(self.running_command_threads)) + "}}xx", log_level=3)
        #     for t in self.running_command_threads:
        #         try:
        #             t.join(3)
        #             if t.is_alive():
        #                 # Still alive? kill it
        #                 p("}}rnThread hasn't exited yet (" + t.name + ")}}xx")
        #                 t.stop()
        #         except Exception as ex:
        #             p("}}rnError trying to join thread!}}xx\n" + str(ex), log_level=1)
        # except Exception as ex:
        #     p("}}rb Unknown exception when shutting down threads }}xx\n" + \
        #         str(ex), log_level=1)
        # p("}}cn***** Threads cleaned up. *****}}xx", log_level=3)
        try:
            # Join the command queue thread
            if not OPEService._COMMAND_QUEUE_THREAD is None:
                OPEService._COMMAND_QUEUE_THREAD.join(3)
                if OPEService._COMMAND_QUEUE_THREAD.is_alive():
                    # Hard kill
                    p("}}rnThread hasn't exited yet (" + OPEService._COMMAND_QUEUE_THREAD.name + ")}}xx")
                    OPEService._COMMAND_QUEUE_THREAD.stop()
        except Exception as ex:
            p("}}rb Unknown exception when shutting down threads }}xx\n" + \
                 str(ex), log_level=1)
        p("}}cb***** OPEService Fully Stopped *****}}xx", log_level=1)

    def main(self):
    
        rc = None
        
        # Loop until we get the "Stop" signal from the service
        while self.isAlive is True and rc != win32event.WAIT_OBJECT_0:
            try:
                # Decide if it is time to run each command yet.
                for cmd in OPEService._COMMANDS_TO_RUN:
                    # run_command will check if it is time to run the command yet
                    self.run_command(cmd, force_run=False)
                
                # See if "stop" has been signaled, or wait for the timeout if it hasn't
                timeout_wait = OPEService._WAIT_TIMEOUT_MSEC # in miliseconds
                # This also pauses the app so we aren't eating up extra CPU
                rc = win32event.WaitForSingleObject(self.hWaitStop, timeout_wait)
                # Do we need a time sleep also?
                # time.sleep(0.5)
            except Exception as ex:
                p("}}rbFATAL ERROR - main loop blew up, this shouldn't happen.}}xx")
                p("}}yb" + str(ex) + "}}xx")
                p("}}yn" + traceback.format_exc() + "}}xx")

        p("}}cnExiting main loop}}xx", log_level=3)
        
        

if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(OPEService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as ex:
            p("}}rbUnknown Exception! }}xx\n" + str(ex))
            #sys.exit(2)
            os._exit(2)
    else:
        try:
            win32serviceutil.HandleCommandLine(OPEService)
        except Exception as ex:
            p("}}rbUnknown Exception! }}xx\n" + str(ex))
            #sys.exit(2)
            os._exit(2)

