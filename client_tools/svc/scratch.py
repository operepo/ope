import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import datetime
import sys
import os
import logging
import random
from win32com.shell import shell, shellcon
import ntsecuritycon
import win32security
import win32api
import win32gui
import win32ui
import win32con
import win32gui_struct
import win32ts
import win32process
import win32profile
import ctypes
import wmi

# TODO - Set recovery options for service so it restarts on failure

# Most event notification support lives around win32gui
GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"

ROOT_FOLDER = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
TMP_FOLDER = os.path.join(ROOT_FOLDER, "tmp")
LOG_FOLDER = os.path.join(TMP_FOLDER, "log")
SCREEN_SHOTS_FOLDER = os.path.join(TMP_FOLDER, "screen_shots")
BINARIES_FOLDER = os.path.join(ROOT_FOLDER, "ope_laptop_binaries")

EVERYONE, domain, type = win32security.LookupAccountName("", "Everyone")
ADMINISTRATORS, domain, type = win32security.LookupAccountName("", "Administrators")
# CURRENT_USER, domain, type = win32security.LookupAccountName("", win32api.GetUserName())
CURRENT_USER = None
try:
    CURRENT_USER, domain, type = win32security.LookupAccountName("", "huskers")
except:
    CURRENT_USER = None
if CURRENT_USER is None:
    try:
        CURRENT_USER, domain, type = win32security.LookupAccountName("", "ray")
    except:
        CURRENT_USER = None
SYSTEM_USER, domain, type = win32security.LookupAccountName("", "System")


# Disable ALL nics if this is set
DISABLE_ALL_NICS = False
DEBUG_NICS = False
if os.path.isfile(os.path.join(ROOT_FOLDER, ".debug_nics")):
    DEBUG_NICS = True
# Disable sshot if this is set
DISABLE_SSHOT = False
if os.path.isfile(os.path.join(ROOT_FOLDER, ".disable_sshot")):
    DISABLE_SSHOT = True

system_nics = ["WAN Miniport (IP)", "WAN Miniport (IPv6)", "WAN Miniport (Network Monitor)",
                   "WAN Miniport (PPPOE)", "WAN Miniport (PPTP)", "WAN Miniport (L2TP)", "WAN Miniport (IKEv2)",
                   "WAN Miniport (SSTP)", "Microsoft Wi-Fi Direct Virtual Adapter", "Teredo Tunneling Pseudo-Interface",
                   "Microsoft Kernel Debug Network Adapter",
                  ]
approved_nics = ["Realtek USB GbE Family Controller",
                 "Thinkpad USB 3.0 Ethernet Adapter"]
if DEBUG_NICS is True:
    # Add these nics so we don't cut off network on our dev machines
    approved_nics.append("Intel(R) 82579LM Gigabit Network Connection")
    approved_nics.append("150Mbps Wireless 802.11bgn Nano USB Adapter")
    approved_nics.append("Intel(R) PRO/1000 MT Network Connection")
    approved_nics.append("Intel(R) Centrino(R) Wireless-N 1000")


def show_cacls(filename):
    print("\n\n")    
    for line in os.popen("cacls %s" % filename).read().splitlines():
        print(line)


def set_ope_permissions():
    global ROOT_FOLDER, LOG_FOLDER, SCREEN_SHOTS_FOLDER, BINARIES_FOLDER, TMP_FOLDER

    # Make sure folders exits
    if not os.path.isdir(ROOT_FOLDER):
        os.makedirs(ROOT_FOLDER)
    if not os.path.isdir(TMP_FOLDER):
        os.makedirs(TMP_FOLDER)
    if not os.path.isdir(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)
    if not os.path.isdir(SCREEN_SHOTS_FOLDER):
        os.makedirs(SCREEN_SHOTS_FOLDER)
    if not os.path.isdir(BINARIES_FOLDER):
        os.makedirs(BINARIES_FOLDER)

    # Make sure the ope-sshot.log file exists so we can set permissions on it later
    if not os.path.isfile(os.path.join(LOG_FOLDER, "ope-sshot.log")):
        f = open(os.path.join(LOG_FOLDER, "ope-sshot.log"), "w")
        f.close()

    # --- Set permissions on OPE folder - viewable by not writable
    # Set inheritance flags
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    sd = win32security.GetFileSecurity(ROOT_FOLDER, win32security.DACL_SECURITY_INFORMATION)
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    if not CURRENT_USER is None:
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, CURRENT_USER)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags,
                               ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
                               EVERYONE)
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(ROOT_FOLDER, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)

    # --- Set permissions on TMP folder - viewable by not writable
    # Set inheritance flags
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    sd = win32security.GetFileSecurity(TMP_FOLDER, win32security.DACL_SECURITY_INFORMATION)
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    if not CURRENT_USER is None:
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, CURRENT_USER)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags,
                               ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
                               EVERYONE)
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(TMP_FOLDER, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)


    # --- Set permissions on ope_laptop_binaries folder - viewable by not writable
    # Set inheritance flags
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    sd = win32security.GetFileSecurity(BINARIES_FOLDER, win32security.DACL_SECURITY_INFORMATION)
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    if not CURRENT_USER is None:
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, CURRENT_USER)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags,
                               ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
                               EVERYONE)
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    # Set on all folders
    win32security.SetFileSecurity(BINARIES_FOLDER, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)
    for root, dirs, files in os.walk(BINARIES_FOLDER, topdown=False):
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

    # win32security.TreeSetNamedSecurityInfo(BINARIES_FOLDER, win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, None, None, sd, None)


    # --- Set permissions on the log folder - create file or append only
    # Set inheritance flags
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    sd = win32security.GetFileSecurity(LOG_FOLDER, win32security.DACL_SECURITY_INFORMATION)
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    if not CURRENT_USER is None:
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, CURRENT_USER)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, flags,
                             ntsecuritycon.FILE_ADD_FILE | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
                             EVERYONE)
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(LOG_FOLDER, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)


    # --- Set permissions on the log file for screen shots - append only
    # Set inheritance flags
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    sd = win32security.GetFileSecurity(os.path.join(LOG_FOLDER, "ope-sshot.log"), win32security.DACL_SECURITY_INFORMATION)
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    if not CURRENT_USER is None:
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, CURRENT_USER)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, flags,
                             ntsecuritycon.FILE_APPEND_DATA | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
                             EVERYONE)
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(os.path.join(LOG_FOLDER, "ope-sshot.log"), win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)



    # --- Set permissions on the sshot folder - let students create but not modify/delete sshots
    # Set inheritance flags
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    sd = win32security.GetFileSecurity(SCREEN_SHOTS_FOLDER, win32security.DACL_SECURITY_INFORMATION)

    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    if not CURRENT_USER is None:
        dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS, flags, ntsecuritycon.FILE_ALL_ACCESS, CURRENT_USER)
    dacl.AddAccessAllowedAceEx(win32security.ACL_REVISION, flags,
                             ntsecuritycon.FILE_ADD_FILE  | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
                             EVERYONE)
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(SCREEN_SHOTS_FOLDER, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, sd)

    # Possible to set whole tree?
    # win32security.TreeSetNamedSecurityInfo(folder, win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, None, None, sd, None)


def scan_com_ports():
    # TODO - Need Debug
    # Use WMI to pull a list of com ports
    w = wmi.WMI()

    logging.info("Scanning USB/Serial COM Ports...")

    # Scan for PNP Devices that are ports
    for port in w.Win32_PNPEntity(PNPClass="Ports"):
        logging.info("PNP COM Port Found: " + str(port.name))
        if port.Status == "OK":
            # Port is on and working - turn it off
            logging.info("COM Port " + str(port.Caption) + " is on - disabling...")
            try:
                port.Disable()
            except Exception as ex:
                logging.info("ERROR!!! " + str(ex))
        else:
            logging.info("COM Port " + str(port.Caption) + " is off...")

    # Scan for Serial devices (may not be PNP)
    for port in w.Win32_SerialPort():
        print("Serial Port Found: " + str(port.name))
        if port.Status == "OK":
            logging.info("Serial Port " + str(port.Caption) + " is on - disabling...")
            try:
                port.Disable()
            except Exception as ex:
                logging.info("ERROR!!! " + str(ex))
        else:
            logging.info("Serial Port " + str(port.Caption) + " is off...")

    return


def scanNics():
    # May need to call this before calling this function so that COM works
    # pythoncom.CoInitialize() - called in the main function
    global DISABLE_ALL_NICS, system_nics, approved_nics

    if DISABLE_ALL_NICS is True:
        approved_nics = []

    logging.info("scanning for unauthorized nics...")
        
    import win32com.client
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_NetworkAdapter")
    for objItem in colItems:
        if objItem.Name in approved_nics:
            # logging.info("***Device found - on approved list: " + str(objItem.Name) + str(objItem.NetConnectionID))
            dev_id = objItem.NetConnectionID
            if dev_id:
                logging.info("     ---> !!! Approved device !!!, enabling..." + str(dev_id))
                cmd = "netsh interface set interface \"" + dev_id + "\" admin=ENABLED"
                # print(cmd)
                os.system(cmd)
            else:
                # print("     ---> unauthorized, not plugged in...")
                pass
            continue
        elif objItem.Name in system_nics:
            # logging.info("***Device found - system nic - ignoring: " + str(objItem.Name))
            continue
        else:
            # logging.info("***Device found :" + str(objItem.Name))
            dev_id = objItem.NetConnectionID
            if dev_id:
                logging.info("     ---> !!! unauthorized !!!, disabling..." + str(dev_id))
                cmd = "netsh interface set interface \"" + dev_id + "\" admin=DISABLED"
                # print(cmd)
                os.system(cmd)
            else:
                # print("     ---> unauthorized, not plugged in...")
                pass
            continue

        # print("========================================================")
        # print("Adapter Type: ", objItem.AdapterType)
        # print("Adapter Type Id: ", objItem.AdapterTypeId)
        # print("AutoSense: ", objItem.AutoSense)
        # print("Availability: ", objItem.Availability)
        # print("Caption: ", objItem.Caption)
        # print("Config Manager Error Code: ", objItem.ConfigManagerErrorCode)
        # print("Config Manager User Config: ", objItem.ConfigManagerUserConfig)
        # print("Creation Class Name: ", objItem.CreationClassName)
        # print("Description: ", objItem.Description)
        # print("Device ID: ", objItem.DeviceID)
        # print("Error Cleared: ", objItem.ErrorCleared)
        # print("Error Description: ", objItem.ErrorDescription)
        # print("Index: ", objItem.Index)
        # print("Install Date: ", objItem.InstallDate)
        # print("Installed: ", objItem.Installed)
        # print("Last Error Code: ", objItem.LastErrorCode)
        # print("MAC Address: ", objItem.MACAddress)
        # print("Manufacturer: ", objItem.Manufacturer)
        # print("Max Number Controlled: ", objItem.MaxNumberControlled)
        # print("Max Speed: ", objItem.MaxSpeed)
        # print("Name: ", objItem.Name)
        # print("Net Connection ID: ", objItem.NetConnectionID)
        # print("Net Connection Status: ", objItem.NetConnectionStatus)
        # z = objItem.NetworkAddresses
        # if z is None:
        #    a = 1
        # else:
        #    for x in z:
        #        print("Network Addresses: ", x)
        # print("Permanent Address: ", objItem.PermanentAddress)
        # print("PNP Device ID: ", objItem.PNPDeviceID)
        # z = objItem.PowerManagementCapabilities
        # if z is None:
        #    a = 1
        # else:
        #    for x in z:
        #        print("Power Management Capabilities: ", x)
        # print("Power Management Supported: ", objItem.PowerManagementSupported)
        # print("Product Name: ", objItem.ProductName)
        # print("Service Name: ", objItem.ServiceName)
        # print("Speed: ", objItem.Speed)
        # print("Status: ", objItem.Status)
        # print("Status Info: ", objItem.StatusInfo)
        # print("System Creation Class Name: ", objItem.SystemCreationClassName)
        # print("System Name: ", objItem.SystemName)
        # print("Time Of Last Reset: ", objItem.TimeOfLastReset)


class OPEService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'OPEService'
    _svc_display_name_ = 'OPEService'
    _svc_description_ = "Open Prison Education Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
        socket.setdefaulttimeout(60)
        self.isAlive = True
        
        # Setup data folders and set permissions
        set_ope_permissions()

        # Setup logging
        logging.basicConfig(
            filename=os.path.join(LOG_FOLDER, 'ope-service.log'),
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='[ope-sshot] %(asctime)-15s %(levelname)-7.7s %(message)s'
        )
        logging.info("service init")

        # register for a device notification - we pass our service handle
        # instead of a window handle.
        filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
                                        GUID_DEVINTERFACE_USB_DEVICE)
        self.hdn = win32gui.RegisterDeviceNotification(self.ssh, filter,
                                    win32con.DEVICE_NOTIFY_SERVICE_HANDLE)

    # Override the base class so we can accept additional events.
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
    
        # All extra events are sent via SvcOtherEx (SvcOther remains as a
    # function taking only the first args for backwards compat)
    def SvcOtherEx(self, control, event_type, data):
        # This is only showing a few of the extra events - see the MSDN
        # docs for "HandlerEx callback" for more info.
        if control == win32service.SERVICE_CONTROL_DEVICEEVENT:
            info = win32gui_struct.UnpackDEV_BROADCAST(data)
            msg = "A device event occurred: %x - %s" % (event_type, info)
            scanNics()
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

        logging.info("Event " + msg)
        servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0xF000,  # generic message
                (msg, '')
                )

    def SvcStop(self):
        self.isAlive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        self.isAlive = True
        logging.info("Service running")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()
        # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        # Write a stop message.
        logging.info("Service Stopped")
        servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
                )

    def runScreenShotApp3_old(self):
        # Get the current security token
        token = win32security.OpenProcessToken(win32process.GetCurrentProcess(),
                                               win32security.TOKEN_ALL_ACCESS)

        # Make a copy
        #token2 = win32security.DuplicateToken(token)
        token2 = win32security.DuplicateTokenEx(token,
                                                win32security.SecurityImpersonation,
                                                win32security.TOKEN_ALL_ACCESS,
                                                win32security.TokenPrimary)

        # Find the session id - we will grab the console/keyboard
        #proc_id = win32process.GetCurrentProcessId()
        #session_id = win32ts.ProcessIdToSessionId(proc_id)
        session_id = win32ts.WTSGetActiveConsoleSessionId()

        # Make this token target our session
        win32security.SetTokenInformation(token2, win32security.TokenSessionId, session_id)

    def runScreenShotApp(self):
        global DISABLE_SSHOT
        if DISABLE_SSHOT is True:
            return
    
        # Get the session id for the console
        session_id = win32ts.WTSGetActiveConsoleSessionId()
        if session_id == 0xffffffff:
            # User not logged in right now?
            logging.info("No console user")
            return None

        # logging.info("Got Console: " + str(session_id))

        # Login to the terminal service to get the user token for the console id
        svr = win32ts.WTSOpenServer(".")
        user_token = win32ts.WTSQueryUserToken(session_id)
        # logging.info("User Token " + str(user_token))

        # Copy the token
        user_token_copy = win32security.DuplicateTokenEx(user_token,
                                                win32security.SecurityImpersonation,
                                                win32security.TOKEN_ALL_ACCESS,
                                                win32security.TokenPrimary)

        # Put this token in the logged in session
        win32security.SetTokenInformation(user_token_copy, win32security.TokenSessionId, session_id)

        # Switch to the user
        # win32security.ImpersonateLoggedOnUser(user_token)
        # logging.info("Impersonating " + win32api.GetUserName())

        # Run the screen shot app
        # app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        # cmd = os.path.join(app_path, "sshot\\dist\\sshot.exe")
        cmd = os.path.join(ROOT_FOLDER, "Services\\sshot\\sshot.exe")  # "c:\\programdata\\ope\\bin\\sshot.exe"
        # cmd = "cmd.exe"
        logging.info("Running sshot app " + cmd)

        # Use win create process function
        si = win32process.STARTUPINFO()
        si.dwFlags = win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_NORMAL
        # si.lpDesktop = "WinSta0\Default"  # WinSta0\Winlogon
        si.lpDesktop = ""

        # Setup envinroment for the user
        environment = win32profile.CreateEnvironmentBlock(user_token, False)

        try:
            (hProcess, hThread, dwProcessId, dwThreadId) = win32process.CreateProcessAsUser(user_token_copy,
                                             None,   # AppName (really command line, blank if cmd line supplied)
                                             "\"" + cmd + "\"",  # Command Line (blank if app supplied)
                                             None,  # Process Attributes
                                             None,  # Thread Attributes
                                             0,  # Inherits Handles
                                             win32con.NORMAL_PRIORITY_CLASS,  # or win32con.CREATE_NEW_CONSOLE,
                                             environment,  # Environment
                                             os.path.dirname(cmd),  # Curr directory
                                             si)  # Startup info

            # logging.info("Process Started: " + str(dwProcessId))
            # logging.info(hProcess)
        except Exception as e:
            logging.info("Error launching process: " + str(e))

        # logging.info(os.system(cmd))

        # Return us to normal security
        # win32security.RevertToSelf()

        # Cleanup
        win32ts.WTSCloseServer(svr)
        user_token.close()
        user_token_copy.close()

        return

    def runScreenShotApp2_old(self):
        console_id = win32ts.WTSGetActiveConsoleSessionId()
        if console_id == 0xffffffff:
            # User not logged in right now?
            logging.info("No console user")
            return None

        dc = None

        logging.info("Got console: " + str(console_id))

        # Get processes running on this console
        svr = win32ts.WTSOpenServer(".")
        user_token = win32ts.WTSQueryUserToken(console_id)
        logging.info("User Token " + str(user_token))

        # hwnd = win32gui.GetDC(win32con.HWND_DESKTOP)  # win32gui.GetDesktopWindow()
        # dc = ctypes.windll.user32.GetDC(win32con.HWND_DESKTOP)
        # logging.info("DC before impersonation " + str(dc))
        # win32gui.ReleaseDC(win32con.HWND_DESKTOP, dc)

        # Switch to the user
        win32security.ImpersonateLoggedOnUser(user_token)
        logging.info("Impersonating " + win32api.GetUserName())

        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        cmd = os.path.join(app_path, "sshot\\dist\\sshot.exe")
        logging.info("Running sshot app " + cmd)
        logging.info(os.system(cmd))

        # hwnd = ctypes.windll.user32.GetDC(win32con.HWND_DESKTOP)
        # logging.info("HWND after impersonation " + str(hwnd))
        # ps_list = win32ts.WTSEnumerateProcesses(svr, 1, 0)
        # for ps in ps_list:
        #    logging.info("PS " + str(ps))
        win32ts.WTSCloseServer(svr)

        # Revert back to normal user
        win32security.RevertToSelf()
        user_token.close()

        return

    def grabScreenShot_old(self):
        # Grab the screen shot and save it to the logs folder
        # Get the hwnd for the current desktop window
        try:
            hwnd = win32gui.GetDesktopWindow()
            # hwnd = self.getDesktopHWND()
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            w = r - l
            h = b - t
            logging.info("SC - HWND " + str(hwnd) + " " + str(w) + "/" + str(h))
            
            dc = win32gui.GetDC(win32con.HWND_DESKTOP)
            logging.info("DC " + str(dc))
            
            dcObj = win32ui.CreateDCFromHandle(dc)
            drawDC = dcObj.CreateCompatibleDC()
            logging.info("drawDC " + str(drawDC))
            
            # cDC = dcObj.CreateCompatibleDC() # Do we need this since it is the desktop dc?
            bm = win32ui.CreateBitmap()
            bm.CreateCompatibleBitmap(dcObj, w, h)
            drawDC.SelectObject(bm)
            drawDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
            
            bm.SaveBitmapFile(drawDC, os.path.join(SCREEN_SHOTS_FOLDER, "test.jpeg"))
            
            win32gui.DeleteObject(bm.GetHandle())
            drawDC.DeleteDC()
            dcObj.DeleteDC()
            win32gui.ReleaseDC(win32con.HWND_DESKTOP, dc)
            
            # dc = win32gui.GetWindowDC(hwnd)
            # logging.info("DC " + str(dc))
            # dcObj = win32ui.CreateDCFromHandle(dc)
            # logging.info("dcObj " + str(dcObj))
            # cDC = dcObj.CreateCompatibleDC()
            # logging.info("cDC " + str(cDC))
            # bm = win32ui.CreateBitmap()
            # logging.info("bm " + str(bm))
            # bm.CreateCompatibleBitmap(dcObj, w, h)
            # cDC.SelectObject(bm)
            # r = cDC.BitBlt((0,0), (w,h), dcObj, (0,0), win32con.SRCCOPY)
            # logging.info("bitblt " + str(r))
            # bm.SaveBitmapFile(cDC, os.path.join(SCREEN_SHOTS_FOLDER, "test.jpeg"))
            # dcObj.DeleteDC()
            # cDC.DeleteDC()
            # win32gui.ReleaseDC(hwnd, dc)
            # win32gui.DeleteObject(bm.GetHandle())
        except Exception as ex:
            logging.info("Error grabbing screenshot: " + str(ex))
        
        # m = ImageGrab.grab()

        # Save the file
        # p = os.path.join(SCREEN_SHOTS_FOLDER, str(datetime.datetime.now()) + ".png")
        # im.save(p, optimize=True)

    def main(self):
        rc = None
        nic_scan_time = 0
        sshot_time = time.time() + 60 # Start by waiting at least a minute before trying
        # Need this so scanNics doesn't fail
        pythoncom.CoInitialize()
        
        while rc != win32event.WAIT_OBJECT_0:

            # Grab screen shots
            if sshot_time - time.time() < 0:
                # Reset the sshot_timer = now + 15 secs + up to 10 minutes rand value
                sshot_time = time.time() + 15 + random.randint(0, 600)
                # Time to take another screen shot
                try:
                    self.runScreenShotApp()
                except Exception as ex:
                    logging.error("Error grabbing screen shot: " + str(ex))

            # Scan for inserted NICS
            if time.time() - nic_scan_time > 60:
                scanNics()
                nic_scan_time = time.time()

            # Grab event logs

            # Grab firewall logs

            # Run virus scanner

            # Security checks - is current user the correct user?

            # Is online?

            # block for 24*60*60 seconds and wait for a stop event
            # it is used for a one-day loop
            rest = 5  # * 1000  # 24*60*60*1000
            rc = win32event.WaitForSingleObject(self.hWaitStop, rest)
            time.sleep(0.5)
        
        # Cleanup
        pythoncom.CoUninitialize()
        
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(OPEService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(OPEService)
