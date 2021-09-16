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


















from firmware_variables import *
from firmware_variables.load_option  import LoadOptionAttributes, LoadOption
from firmware_variables.device_path import DevicePathList, DevicePath, DevicePathType, MediaDevicePathSubtype, EndOfHardwareDevicePathSubtype
from firmware_variables.utils import verify_uefi_firmware, string_to_utf16_bytes, utf16_string_from_bytes
import struct
import collections
import uuid
import sys
import io
import traceback
import win32file
import win32con
import winioctlcon
import pythoncom
import wmi
import ctypes
from ctypes import wintypes
import winerror

kernel32 = ctypes.WinDLL('kernel32')

# Register wapi functions
kernel32.FindFirstVolumeW.restype = wintypes.HANDLE
kernel32.FindNextVolumeW.argtypes = (wintypes.HANDLE,
    wintypes.LPWSTR,
    wintypes.DWORD)
kernel32.FindVolumeClose.argtypes = (wintypes.HANDLE,)


def FindFirstVolume():
    v_name = ctypes.create_unicode_buffer(" " *  255)
    h = kernel32.FindFirstVolumeW(v_name, 255)
    if h == win32file.INVALID_HANDLE_VALUE:
        raise Exception("Invalid Handle for FindFirstVolume")
    
    return h, v_name.value

def FindNextVolume(h):
    v_name = ctypes.create_unicode_buffer(" " *  255)
    if kernel32.FindNextVolumeW(h, v_name, 255) != 0:
        return v_name.value
    
    # Error if we get here
    e = ctypes.GetLastError()
    if e == winerror.ERROR_NO_MORE_FILES:
        FindVolumeClose(h)
        return None
    raise Exception("Error calling FindNextVolumeW (%s)" % e)
    
def FindVolumeClose(h):
    if kernel32.FindVolumeClose(h) == 0:
        # Failed?
        raise Exception("FindVolumeClose failed on handle (%s)" % h)
    



# Boot Variables
# Boot#### - #### Hex value, no 0x or h, for the item
# BootCurrent - Option selected for the current boot
# BootNext - Boot option for next boot only
# BootOrder - List of boot options in order
# BootOrderSupport - Types of boot options supported by the boot manager (read only)

# Driver#### - Driver load option
# DriverOrder - Ordered list of drivers to load
 
"""
efi boot item:
struct {
  UINT32 // Attributes - bit mask
  UINT16 // File Path List Length  - len in bytes of whole file path list Optional Data starts at sizeof(UINT32) + sizeof(UINT16) + strsize(Description) + FilePathListLengh
  CHAR16  // Description - Null term string
  EFI_DEVICE_PATH_PROTOCOL  // FilePathList[]
  UINT8     //Optional Data - calculate size from starting offset to size of whole load_option structure
}
  

"""

#pythoncom.CoInitialize()
#pythoncom.CoUnInitialize()

DISKDRIVES_QUERY = "SELECT * FROM Win32_DiskDrive"
VOLUME_QUERY = "SELECT * FROM Win32_Volume"
VOLUME_CLUSTER_SIZE_QUERY = "SELECT Name, Blocksize FROM Win32_Volume WHERE FileSystem='NTFS'"
DISKDRIVE_TO_DISKPARTITIONS_QUERY = r'SELECT * FROM Win32_DiskDriveToDiskPartition WHERE Antecedent="{}"'
DISKPARTITION_QUERY = r'SELECT * FROM Win32_DiskPartition WHERE DeviceID={}'


class PhysicalDrive():
    DRIVES = dict()
    
    def __init__(self, drive_id=0, wmi_obj=None):
        self.drive_id = drive_id
        self.win_path = r"\\.\PHYSICALDRIVE" + str(self.drive_id)
        self.wmi_obj = wmi_obj
    
    def get_partitions(self):
        
        partitions = list()
        
        # Get the mapping from disk to partition
        res = self.wmi_obj.associators("MSFT_DiskToPartition")
        #self.wmi_obj.associators("Win32_DiskDriveToDiskPartition")
        
        for r in res:
            #print(r)
            partitions.append(r)
        
        return partitions
    
    def IsBoot(self):
        if self.wmi_obj is None:
            print("WMI OBJ is NULL!")
            return False
        
        return self.wmi_obj.IsBoot
        
    def __repr__(self):
        DeviceID = None
        guid = None
        if self.wmi_obj is not None:
            DeviceID = self.wmi_obj # self.wmi_obj.DeviceID
            #guid = self.wmi_obj.Guid
        return "Drive <" + str(self.win_path) + ", " + str(DeviceID) + ">"
    
    @staticmethod
    def get_drives():
        # https://stackoverflow.com/questions/56784915/python-wmi-can-we-really-say-that-c-is-always-the-boot-drive
        w = wmi.WMI(namespace='root/Microsoft/Windows/Storage')
        res = w.MSFT_Disk() #w.Win32_DiskDrive()
        PhysicalDrive.DRIVES = dict()
        for r in res:
            #print(r)
            disk_number = r.Number # r.Index
            physical_path = r'\\.\PHYSICALDRIVE' + str(disk_number)  # r.DeviceID
            d = PhysicalDrive(disk_number, r)
            PhysicalDrive.DRIVES[physical_path] = d
        
        return PhysicalDrive.DRIVES
        
        
        

def findVolumeGuids_broken():
    DiskExtent = collections.namedtuple(
        'DiskExtent', ['DiskNumber', 'StartingOffset', 'ExtentLength'])
    Volume = collections.namedtuple(
        'Volume', ['Guid', 'MediaType', 'DosDevice', 'Extents'])
    found = []
    h, guid = FindFirstVolume()
    while h and guid:
        #print (guid)
        #print (guid, win32file.GetDriveType(guid),
        #       win32file.QueryDosDevice(guid[4:-1]))
        hVolume = win32file.CreateFile(
            guid[:-1], win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None, win32con.OPEN_EXISTING, win32con.FILE_ATTRIBUTE_NORMAL,  None)
        extents = []
        driveType = win32file.GetDriveType(guid)
        if driveType in [win32con.DRIVE_REMOVABLE, win32con.DRIVE_FIXED]:
            x = win32file.DeviceIoControl(
                hVolume, winioctlcon.IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS,
                None, 512, None)
            instream = io.BytesIO(x)
            numRecords = struct.unpack('<q', instream.read(8))[0]
            fmt = '<qqq'
            sz = struct.calcsize(fmt)
            while 1:
                b = instream.read(sz)
                if len(b) < sz:
                    break
                rec = struct.unpack(fmt, b)
                extents.append( DiskExtent(*rec) )
        vinfo = Volume(guid, driveType, win32file.QueryDosDevice(guid[4:-1]),
                       extents)
        found.append(vinfo)
        guid = FindNextVolume(h)
    return found

def find_efi_partition():
        
    drives = PhysicalDrive.get_drives()
    for drive_path in drives:
        drive = drives[drive_path]
        #print(drive)
        if drive.IsBoot() == True:
            # Found the boot drive, look for the EFI partition
            partitions = drive.get_partitions()
            #print(partitions)
            for part in partitions:
                if part.GptType == "{c12a7328-f81f-11d2-ba4b-00a0c93ec93b}":
                    print("Found EFI Part: " + part.Guid)
                    print(part)
                    sector_size = int(drive.wmi_obj.PhysicalSectorSize)
                    part_starting_sector = int(int(part.Offset) / sector_size)
                    part_size = int(int(part.Size) / sector_size)
                    part_guid = part.Guid
                    part_number = part.PartitionNumber
                    return (part, part_guid, part_number, part_starting_sector, part_size)
                                    
    
    print("ERROR - Unable to find EFI partition!")
    
    return None

def parse_uefi_data(data):
    data_len = len(data)
    import locale   
    ret = str(data, "utf-16-le" )  # utf8, utf16, cp437
    #ret = str(struct.unpack(str(data_len)+"B", data), "UTF-8") #.decode("UTF-8")
    #ret = struct.unpack("B", data)  #.decode("UTF-16-LE")
    #print(ret)
    return ret

# Get all entries
with privileges():
    try:
        verify_uefi_firmware()
    except:
        print("Not UEFI Bios!")
        sys.exit(0)

    found_entries = dict()
    
    # Always BCDOBJECT={9dea862c-5cdd-4e70-acc1-f32b344d4795} w some other data??? - is boot manager id
    WIN_OPTIONAL_DATA = b'WINDOWS\x00\x01\x00\x00\x00\x88\x00\x00\x00x\x00\x00\x00B\x00C\x00D\x00O\x00B\x00J\x00E\x00C\x00T\x00=\x00{\x009\x00d\x00e\x00a\x008\x006\x002\x00c\x00-\x005\x00c\x00d\x00d\x00-\x004\x00e\x007\x000\x00-\x00a\x00c\x00c\x001\x00-\x00f\x003\x002\x00b\x003\x004\x004\x00d\x004\x007\x009\x005\x00}\x00\x00\x00.\x00\x01\x00\x00\x00\x10\x00\x00\x00\x04\x00\x00\x00\x7f\xff\x04\x00'
    #b'WINDOWS\x00\x01\x00\x00\x00\x88\x00\x00\x00x\x00\x00\x00B\x00C\x00D\x00O\x00B\x00J\x00E\x00C\x00T\x00=\x00{\x009\x00d\x00e\x00a\x008\x006\x002\x00c\x00-\x005\x00c\x00d\x00d\x00-\x004\x00e\x007\x000\x00-\x00a\x00c\x00c\x001\x00-\x00f\x003\x002\x00b\x003\x004\x004\x00d\x004\x007\x009\x005\x00}\x00\x00\x00.\x00\x01\x00\x00\x00\x10\x00\x00\x00\x04\x00\x00\x00\x7f\xff\x04\x00'
    #b'WINDOWS\x00\x01\x00\x00\x00\x88\x00\x00\x00x\x00\x00\x00B\x00C\x00D\x00O\x00B\x00J\x00E\x00C\x00T\x00=\x00{\x009\x00d\x00e\x00a\x008\x006\x002\x00c\x00-\x005\x00c\x00d\x00d\x00-\x004\x00e\x007\x000\x00-\x00a\x00c\x00c\x001\x00-\x00f\x003\x002\x00b\x003\x004\x004\x00d\x004\x007\x009\x005\x00}\x00\x00\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x04\x00\x00\x00\x7f\xff\x04\x00'
    WIN_DEVICE_PATH_DATA = string_to_utf16_bytes("\\EFI\\Microsoft\\Boot\\bootmgfw.efi")
    #b'\x02\x00\x00\x00\x00\x18\x0e\x00\x00\x00\x00\x00\x00 \x03\x00\x00\x00\x00\x00\xfc?\x1bs{\xb5rL\x91\xf7\xbar\xb8\xbe\x11h\x02\x02'
    """
        type -              1 byte - Type 4 - MEDIA_DEVICE_PATH (added during tobytes)
        sub-type -          1 byte - Type 1 - HARD_DRIVE (added during tobytes)
        length -            2 bytes - len of this structure (42 bytes? added during tobytes)
        partition number -  4 bytes - 0 means whole disk, 1 = first part, 1-4 valid for MBR, 1-count valid for GPT
        partition start  -  8 bytes - Starting LBA of partition
        partition size -    8 bytes - Size of part in logical blocks
        Part Signature -    16 bytes - 0 if part type is 0, type 1 = mbr sig in first 4 bytes, type 2= 16 byte signature (guid?)
        part format -       1 byte   - 0x01 - mbr, 0x02 - guid parition
        Sig Type -          1 byte   - 0x00 - no signature, 0x01 - 32 bit signature from address 0x1b8 of type 0x01 mbr, 0x02 - GUID signature
        
        
    """
    boot_part = find_efi_partition()
    if boot_part is None:
        print("Error - Unable to find efi boot part!")
        sys.exit(-1)
    (part, part_guid, part_number, part_starting_sector, part_size) = boot_part
    # bytes_le - little endian for first half bytes
    packed_guid = uuid.UUID(part_guid).bytes_le

    # Pack data into this structure
    # part num - 8 bytes, part_start 8 bytes, part_size 8 bytes, part guid - 16 bytes, part format - 1 byte, sig type - 1 byte
    WIN_HARD_DRIVE_MEDIA_PATH = b''
    WIN_HARD_DRIVE_MEDIA_PATH = struct.Struct("<LQQ16sBB").pack(
        part_number,           # Long - 4  bytes
        part_starting_sector,  # long long - 8 bytes
        part_size,             # long long - 8 bytes
        packed_guid,           # 16 bytes, 
        0x02,                  # 1 byte - 0x01 for mbr, 0x02 for gpt
        0x02,                  # 1 byte - 0x00 none, 0x01 mbr, 0x02 gpt
    )
    
    # Make our default boot option
    ope_entry = LoadOption()
    ope_entry.attributes = LoadOptionAttributes.LOAD_OPTION_ACTIVE
    ope_entry.description="OPE Boot"
    # Add the disk GUID entry
    ope_entry.file_path_list.paths.append(DevicePath(
        DevicePathType.MEDIA_DEVICE_PATH, MediaDevicePathSubtype.HARD_DRIVE, WIN_HARD_DRIVE_MEDIA_PATH
        )
    )
    # Add the file path
    ope_entry.file_path_list.paths.append(DevicePath(
        DevicePathType.MEDIA_DEVICE_PATH, MediaDevicePathSubtype.FILE_PATH, WIN_DEVICE_PATH_DATA
        )
    )
    ope_entry.file_path_list.paths.append(DevicePath(
        DevicePathType.END_OF_HARDWARE_DEVICE_PATH, EndOfHardwareDevicePathSubtype.END_ENTIRE_DEVICE_PATH
    ))
    #ret = ope_entry.file_path_list.set_file_path('\\EFI\\Microsoft\\Boot\\bootmgfw.efi')
    #print(ret)
    #ope_entry.file_path_list.data = WIN_DEVICE_PATH_DATA
    #ope_entry.file_path_list.paths[0].data = WIN_DEVICE_PATH_DATA
    #ope_entry.file_path_list.paths[0].subtype = MediaDevicePathSubtype.HARD_DRIVE
    #ope_entry.optional_data = WIN_OPTIONAL_DATA
    
    #set_parsed_boot_entry(0, ope_entry)
    
    
    # Find all boot entries
    for i in range(0, 24):
        # Get entry
        try:
            parsed_option = get_parsed_boot_entry(i)
            print(str(i) + " - " + parsed_option.description)
            print(parsed_option.file_path_list.paths[0].data)
            print(parsed_option)
            
            #print(parsed_option.attributes)
            print("Device Paths")
            for p in parsed_option.file_path_list.paths:
                print("------")
                print(f"\t{p.path_type}")
                print(f"\t{p.subtype}")
                print(f"\t{p.data}")
            #print(len(parsed_option.file_path_list.paths))
            #if len(parsed_option.file_path_list.paths) > 0:
            #    print(parsed_option.file_path_list.get_file_path())
            #    print(parsed_option.file_path_list.paths[0].path_type)
            #    print(parsed_option.file_path_list.paths[0].subtype)
            
            print(parse_uefi_data(parsed_option.optional_data))
            print(parsed_option.optional_data)
            print("")
            
            if parsed_option.description != "OPE Boot":
                found_entries[parsed_option.description] = parsed_option
        except Exception as ex:
            # Will get errors if we run out of entries. That is OK.
            if "environment option" not in str(ex):
                print(ex)
                traceback.print_exc()
            pass
        
        
    
    # Set our custom entry as first entry
    boot_order = list()
    boot_order.append(0)
    set_parsed_boot_entry(0, ope_entry)
    
    i = 1
    for entry_desc in found_entries:
        entry = found_entries[entry_desc]
        # Add each entry back to the boot entries.
        if entry.description == "UEFI: Realtek USB FE Family Controller":
            entry.attributes = LoadOptionAttributes.LOAD_OPTION_HIDDEN | LoadOptionAttributes.LOAD_OPTION_ACTIVE
        elif entry.description == "UEFI: IP4 Realtek USB FE Family Controller":
            entry.attributes = LoadOptionAttributes.LOAD_OPTION_HIDDEN | LoadOptionAttributes.LOAD_OPTION_ACTIVE
        else:
            entry.attributes = LoadOptionAttributes.LOAD_OPTION_HIDDEN | LoadOptionAttributes.LOAD_OPTION_ACTIVE
        set_parsed_boot_entry(i, entry)
        boot_order.append(i)
        i+=1
    
    # Write the new boot order
    set_boot_order(boot_order)
    
    
    # Get the current list of boot items.
    #for entry_id in get_boot_order():
    #    load_option = get_parsed_boot_entry(entry_id)
    #    print(f"{entry_id} {load_option} {load_option.description}\n\t\t{load_option.optional_data}\n")

    

exit()
with privileges():
    data, attr = get_variable("BootCurrent")
    print(data)
    print(attr)
    
with privileges():
    for entry_id in get_boot_order():
        load_option = get_parsed_boot_entry(entry_id)
        print(f"{entry_id} {load_option}")
        

with privileges():
    # Set our custom order
    boot_order = get_boot_order()
    set_boot_order(boot_order)
    
    boot_entry = get_parsed_boot_entry(boot_order[0])
    print(boot_entry.__dict__)
    
    boot_entry.description="OPE Boot"
    boot_entry.file_path_list.set_file_path(r"\EFI\MICROSOFT\BOOT\BOOTMGWFW.EFI")
    
    set_parsed_boot_entry(0, boot_entry)


with privileges():
    data, attr = get_variable("BootCurrent")
    print(data)
    print(attr)
    
with privileges():
    for entry_id in get_boot_order():
        load_option = get_parsed_boot_entry(entry_id)
        print(f"{entry_id} {load_option}")
        raw_entry = get_boot_entry(entry_id)
        loaded_option = LoadOption.from_bytes(raw_entry)
        loaded_option.attributes = LoadOptionAttributes.LOAD_OPTION_HIDDEN
        print("0x{:04X} {}".format(entry_id, loaded_option))
        

exit()
with privileges():
    ope_id, attr = get_variable("OPE_ID")
    
    if ope_id is None:
        namespace = "{f29e2c32-8cca-44ff-93d7-87195ace38b9}" 
        ope_id = uuid.uuid4()
        set_variable("OPE_ID", ope_id,
            namespace=namespace,
            attributes= Attributes.NON_VOLATILE |
                        Attributes.BOOT_SERVICE_ACCESS |
                        Attributes.RUNTIME_ACCESS
            )
        # delete_variable("OPE_ID", namespace=namespace)
    