# Needed for external stuff?
#import pythoncom

## Service Imports
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

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

# Import local modules
from color import p
import util
from mgmt_RegistrySettings import RegistrySettings
from mgmt_EventLog import EventLog


class OPEService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'OPEService'
    _svc_display_name_ = 'OPEService'
    _svc_description_ = "Open Prison Education Service"

    _svc_instance = None

    _WAIT_TIMEOUT_MSEC = 250

    # GUID to subscribe to - we wan't USB events
    GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
    
    # Track last time the command was run
    _COMMAND_NEXT_RUN_TIMES = {}

    # Threads that are currently running
    _RUNNING_COMMAND_THREADS = {}

    _LOG_INSTANCE = None

    @staticmethod
    def reload_settings():
        p("}}ybRunning reload_sttings}}xx")
        # Reload settings for the service from the registry
        if OPEService._svc_instance is None:
            p("}}rbNo OPEService running? - NOT reloading settings!")
            return False
        
        OPEService._svc_instance.log_event("}}mbReloading Settings}}xx", log_level=4)

        #### Grab settings from the registry

        if OPEService._LOG_INSTANCE is not None:
            # Grab log level
            value_name = "log_level"
            value = RegistrySettings.get_reg_value(app="OPEService",
                value_name=value_name, default=3, value_type="REG_DWORD")
            old_val = OPEService._LOG_INSTANCE.log_level
            if old_val != value:
                OPEService._svc_instance.log_event("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=5)
            OPEService._LOG_INSTANCE.log_level = value

        # Grab how often to run default permissions (registry and ope folder)
        value_name = "set_default_permissions_timer"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default=3600, value_type="REG_DWORD")
        old_val = OPEService._COMMANDS_TO_RUN["set_default_ope_folder_permissions"]["timer"]
        if old_val != value:
            OPEService._svc_instance.log_event("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=5)
        OPEService._COMMANDS_TO_RUN["set_default_ope_folder_permissions"]["timer"] = value
        OPEService._COMMANDS_TO_RUN["set_default_ope_registry_permissions"]["timer"] = value


        # How often should we run reload_settings function?
        value_name = "reload_settings"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default=30, value_type="REG_DWORD")
        old_val = OPEService._COMMANDS_TO_RUN["reload_settings"]["timer"]
        if old_val != value:
            OPEService._svc_instance.log_event("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=5)
        OPEService._COMMANDS_TO_RUN["reload_settings"]["timer"] = value

        # How often should we run scan_nics
        value_name = "scan_nics_frequency"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default=60, value_type="REG_DWORD")
        old_val = OPEService._COMMANDS_TO_RUN["scan_nics"]["timer"]
        if old_val != value:
            OPEService._svc_instance.log_event("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=5)
        OPEService._COMMANDS_TO_RUN["scan_nics"]["timer"] = value


        # How often should we run screen_shot
        value_name = "screen_shot_frequency"
        value = RegistrySettings.get_reg_value(app="OPEService",
            value_name=value_name, default="30-300", value_type="REG_SZ")
        old_val = OPEService._COMMANDS_TO_RUN["screen_shot"]["timer"]
        if old_val != value:
            OPEService._svc_instance.log_event("}}ybNew Setting " + value_name + ": " + str(value) + "}}xx", log_level=5)
        OPEService._COMMANDS_TO_RUN["screen_shot"]["timer"] = value


        return True

    # Command + time to run it
    # -1 - disabled
    # 0 - once at startup
    # int - how often to run (in seconds)
    # "1-10" - String - range for random time to run
    #
    # For cmd = %mgmt% will be translated to the path to the mgmt utility
    # same with %sshot% (sshot shouldn't be needed anymore - run it all through mgmt)
    _COMMANDS_TO_RUN = {
        "set_default_ope_folder_permissions": {
            "cmd": "%mgmt% set_default_ope_folder_permissions",
            "timer": 3600  # Reset perms every hour
        },
        "set_default_ope_registry_permissions": {
            "cmd": "%mgmt% set_default_ope_registry_permissions",
            "timer": 3600  # Reset perms every hour
        },
        "reload_settings": {
            # use.__func__ to access static methods function while defining
            "cmd": reload_settings.__func__,
            "timer": 30
        },
        "scan_nics": {
            "cmd": "%mgmt% scan_nics",
            "timer": 60
        },
        "screen_shot": {
            "cmd": "%mgmt% screen_shot",
            "timer": "30-300"
            #"timer": "60-600"   # 1 - 10 minutes
        }      
        
    }

    def log_event(self, msg, is_error=False, show_in_event_log=True, log_level=3):

        if OPEService._LOG_INSTANCE is None:
            OPEService._LOG_INSTANCE = EventLog(os.path.join(util.LOG_FOLDER, 'ope-service.log'),
                service_name="OPEService")
        
        OPEService._LOG_INSTANCE.log_event(msg, is_error, show_in_event_log, log_level)

        return
        
    def get_next_command_run_time(self, command_name):
        # Default to need to run (1 second ago) - any command that hasn't started yet
        # needs to
        next_run_time = time.time()-1
        
        if command_name in OPEService._COMMAND_NEXT_RUN_TIMES:
            next_run_time = OPEService._COMMAND_NEXT_RUN_TIMES[command_name]
        
        #self.log_event(command_name + " - Next run time: " + str(next_run_time), log_level=4)
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
                    start_int = int(parts[0])
                    end_int = int(parts[1])
                    timer = random.randint(start_int, end_int)
                    self.log_event("Found random range - new timer = +" + str(timer) + " seconds", log_level=4)
                else:
                    # invalid format??
                    self.log_event("Invalid timer format defaulting to 60 seconds? " +
                        str(timer) + " / " + command_name, log_level=2)
                    timer = 60
            
            # Calculate next run time
            if timer != 0:
                next_run_time = time.time() + timer
                OPEService._COMMAND_NEXT_RUN_TIMES[command_name] = next_run_time
                self.log_event("Next run time " + command_name + " (" + str(timer) + " seconds)", log_level=3)
            else:
                # Timer = 0 - set next run to -1 (disabled)
                OPEService._COMMAND_NEXT_RUN_TIMES[command_name] = -1
                self.log_event("Timer = 0 - skipping re-schedule " + command_name, log_level=4)
                pass
        else:
            # Shouldn't be scheduling a command that doesn't exist?
            self.log_event("Trying to schedule a bad command to run? " + command_name, log_level=1)
            
    
    def run_command(self, command_name, args=None, force_run=False):
        # Run the command - if force_run isn't True, it will not run
        # the command if it isn't time yet (it will ignore the call)
        time_to_run = False
        # self.log_event("Run command called: " + command_name)
        
        try:
            # See if it is time to run
            next_run_time = self.get_next_command_run_time(command_name)
            # Time left will be how many seconds to wait - anything = or negative means we are that far past time
            time_left = next_run_time - time.time()
            if next_run_time < 1:
                # Don't run commands w a 0 unless they have force_run on
                pass
            elif time_left <= 0:
                # Need to run command
                time_to_run = True

            if force_run is True:
                time_to_run = True
            
            if time_to_run is True:
                # Start the thread to run the command
                thread_args = dict(command_name=command_name, args=args)
                t = threading.Thread(target=self.run_command_thread, name="OPERunCommandThread", kwargs=thread_args)
                # , daemon=True)
                t.start()
                self.running_command_threads.append(t)
                
                # Re-queue the command if needed
                self.reset_next_command_run_time(command_name)
            else:
                # Note - This will generate a LOT of entries - need to collapse/limit this?
                self.log_event("Not time to run command, ignoring: " + command_name +
                    " (" + str(time_left) + " seconds left)", show_in_event_log=False, log_level=6)
                pass
        except Exception as ex:
            self.log_event("}}rbUnknown Exception! Trying to run command " + command_name + "}}xx\n" + str(ex), log_level=1)
    
    def run_command_thread(self, command_name, args=None):
        # Run the actual command in a different thread so it doesn't
        # block the main app
        
        cmd = OPEService._COMMANDS_TO_RUN[command_name]["cmd"]

         # Is this a function pointer or a command line string?
        if callable(cmd):
            # Function pointer
            self.log_event("}}mbRunning command (function): " + command_name +
                " - (" + str(cmd) + " Args: " + str(args) + ")}}xx",
                log_level=3)
            try:
                r = cmd()
            except Exception as ex:
                self.log_event("}}rb*** ERROR RUNNING FUNCTION ***}}xx\n" + str(ex))
                
        else:
            # Command string
            # Replace %sshot% and %mgmt% w valid paths
            cmd = self.fix_path_variables(cmd)

            self.log_event("}}mbRunning command: " + command_name +
                " - (" + str(cmd) + " Args: " + str(args) + ")}}xx",
                log_level=3)

            # Run the command
            timeout = 20*60 # 20 mins?
            try:
                # Log an error if the process doesn't return 0
                # stdout=PIPE and stderr=STDOUT instead of capture_output=True
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,timeout=timeout, check=False)
                if (proc.returncode == 0):
                    self.log_event("}}mnCommand Results: " + command_name + " - Args: " +
                        str(args) + "}}xx\n" + proc.stdout.decode(), log_level=3)
                else:
                    self.log_event("}}rn*** Command Failed!: " + command_name +
                        "(Return: " + str(proc.returncode) + ") - " + str(args) +
                        " --- }}xx\n" + proc.stdout.decode(), log_level=2)
            except Exception as ex:
                self.log_event("}}rb*** Command Exception! " + command_name + " - " + str(args) + " --- }}xx\n" + \
                    str(ex), log_level=1)
        
        # Have thread remove itself from the list
        self.running_command_threads.remove(threading.current_thread())
        # self.log_event("Command Finished: " + command_name + " - " + str(args))
        
    
    def fix_path_variables(self, cmd):
        #p("util.BINARIES_FOLDER: " + util.BINARIES_FOLDER)

        # Replace variables such as %sshot% and %mgmt% w proper paths
        mgmt_path = os.path.normpath(os.path.join(util.BINARIES_FOLDER, "mgmt/mgmt.exe"))
        sshot_path = os.path.normpath(os.path.join(util.BINARIES_FOLDER, "sshot/sshot.exe"))
        
        cmd = cmd.replace("%mgmt%", mgmt_path)
        cmd = cmd.replace("%sshot%", sshot_path)

        self.log_event("fix_path_variable: " + cmd, log_level=4)

        return cmd
        
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        if OPEService._svc_instance is not None:
            p("}}rbAnother instance of OPEService decteced?!?!? FIX}}xx")
        OPEService._svc_instance = self
                

        self.running_command_threads = []

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
            
            self.log_event("Service now listening for device events", log_level=3)
        except Exception as ex:
            self.log_event("Unknown Error listening for device events " + str(ex), log_level=1)
        
        return

    # All extra events are sent via SvcOtherEx (SvcOther remains as a
    # function taking only the first args for backwards compat)
    def SvcOtherEx(self, control, event_type, data):
        # This is only showing a few of the extra events - see the MSDN
        # docs for "HandlerEx callback" for more info.
        if control == win32service.SERVICE_CONTROL_DEVICEEVENT:
            info = win32gui_struct.UnpackDEV_BROADCAST(data)
            msg = "A device event occurred (running scan_nics): %x - %s" % (event_type, info)
            self.run_command("scan_nics", (event_type, info), force_run=True)
        elif control == win32service.SERVICE_CONTROL_HARDWAREPROFILECHANGE:
            msg = "A hardware profile changed: type=%s, data=%s" % (event_type, data)
        elif control == win32service.SERVICE_CONTROL_POWEREVENT:
            msg = "A power event: setting %s" % data
        elif control == win32service.SERVICE_CONTROL_SESSIONCHANGE:
            # data is a single elt tuple, but this could potentially grow
            # in the future if the win32 struct does
            msg = "Session event: type=%s, data=%s" % (event_type, data)
        else:
            msg = "Other event: code=%d, type=%s, data=%s" \
                  % (control, event_type, data)

        self.log_event("-- Event " + msg, log_level=3)
        

    def SvcStop(self):
        try:
            self.isAlive = False

            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

            win32event.SetEvent(self.hWaitStop)
            self.log_event("Stopping Service", log_level=1)
        except Exception as ex:
            p("}}rbUnknown Exception: }}xx\n" + str(ex), log_level=1)
        
    def SvcDoRun(self):
        self.isAlive = True

        # Make sure we are listening for device insert events
        self.ListenForDeviceEvents()

        # Generic exception catch to protect app
        try:

            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log_event("}}mbOPEService running}}xx", log_level=1)

            # Do we need a seprate event entry for this?
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                                servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))

            self.main()
            # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

            # Write a stop message.
            self.log_event("}}mbOPEService Stopped}}xx", log_level=1)
            # Do we need a seperate event entry for this?
            servicemanager.LogMsg(
                    servicemanager.EVENTLOG_INFORMATION_TYPE,
                    servicemanager.PYS_SERVICE_STOPPED,
                    (self._svc_name_, '')
                    )
        except Exception as ex:
            p("}}rbUnknown Exception: }}xx\n" + str(ex), log_level=1)
            pass
        
        try:
            self.log_event("}}ynCleaning up worker threads: " +
                str(len(self.running_command_threads)) + "}}xx", log_level=3)
            for t in self.running_command_threads:
                try:
                    t.join(30)
                except Exception as ex:
                    self.log_event("}}rnError trying to join thread!}}xx\n" + str(ex), log_level=1)
        except Exception as ex:
            self.log_event("}}rb Unknown exception when shutting down threads }}xx\n" + str(ex), log_level=1)
        self.log_event("}}gnThreads cleaned up.}}xx", log_level=3)

    def main(self):
    
        rc = None
        
        # Loop until we get the "Stop" signal from the service
        while self.isAlive is True and rc != win32event.WAIT_OBJECT_0:

            # Decide if it is time to run each command yet.
            for cmd in OPEService._COMMANDS_TO_RUN:
                # run_command will check if it is time to run the command yet
                self.run_command(cmd, force_run=False)
            
            # See if "stop" has been signaled, or wait for the timeout if it hasn't
            timeout_wait = OPEService._WAIT_TIMEOUT_MSEC # in miliseconds
            # This also pauses the app so we aren't eating up etra CPU
            rc = win32event.WaitForSingleObject(self.hWaitStop, timeout_wait)
            # Do we need a time sleep also?
            # time.sleep(0.5)
        self.log_event("}}gnExiting main loop}}xx", log_level=3)
        
        

if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(OPEService)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as ex:
            p("}}rbUnknown Exception! }}xx\n" + str(ex))
            sys.exit(2)
    else:
        try:
            win32serviceutil.HandleCommandLine(OPEService)
        except Exception as ex:
            p("}}rbUnknown Exception! }}xx\n" + str(ex))
            sys.exit(2)

