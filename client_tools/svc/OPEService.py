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
import PIL
import pyscreenshot as ImageGrab
import ctypes

# TODO - Set recovery options for service so it restarts on failure

# Most event notification support lives around win32gui
GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"

LOG_FOLDER = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
SCREEN_SHOTS_FOLDER = os.path.join(LOG_FOLDER, "screen_shots")

EVERYONE, domain, type = win32security.LookupAccountName("", "Everyone")
ADMINISTRATORS, domain, type = win32security.LookupAccountName("", "Administrators")
CURRENT_USER, domain, type = win32security.LookupAccountName("", win32api.GetUserName())
SYSTEM_USER, domain, type = win32security.LookupAccountName("", "System")

def show_cacls(filename):
    print
    print
    for line in os.popen("cacls %s" % filename).read().splitlines():
        print line

def make_data_folder(folder, allow_add_file=False):
    try:
        os.makedirs(folder)
    except:
        pass
        
    # Set permissions on this folder so that it isn't viewable by students
    sd = win32security.GetFileSecurity(folder, win32security.DACL_SECURITY_INFORMATION)
    
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    #dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_GENERIC_READ, EVERYONE)
    if allow_add_file == True:
        dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_ADD_FILE, EVERYONE)
    #dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_WRITE, CURRENT_USER)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(folder, win32security.DACL_SECURITY_INFORMATION, sd)
    


class OPEService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'OPEService'
    _svc_desplay_name_ = 'OPEService'
    _svc_description_ = "Open Prison Education Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
        socket.setdefaulttimeout(60)
        self.isAlive = True
        
        # Setup data folders
        make_data_folder(LOG_FOLDER)
        make_data_folder(SCREEN_SHOTS_FOLDER, True)
        
        # Setup loggin
        logging.basicConfig(
            filename=os.path.join(LOG_FOLDER, 'ope-service.log'),
            level=logging.DEBUG,
            format='[ope-service] %(levelname)-7.7s %(message)s'
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
                0xF000, #  generic message
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

    def runScreenShotApp(self):
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

        #hwnd = win32gui.GetDC(win32con.HWND_DESKTOP)  # win32gui.GetDesktopWindow()
        #dc = ctypes.windll.user32.GetDC(win32con.HWND_DESKTOP)
        #logging.info("DC before impersonation " + str(dc))
        #win32gui.ReleaseDC(win32con.HWND_DESKTOP, dc)

        # Switch to the user
        win32security.ImpersonateLoggedOnUser(user_token)
        logging.info("Impersonating " + win32api.GetUserName())

        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        cmd = os.path.join(app_path, "sshot\\dist\\sshot.exe")
        logging.info("Running sshot app " + cmd)
        logging.info(os.system(cmd))

        #hwnd = ctypes.windll.user32.GetDC(win32con.HWND_DESKTOP)
        #logging.info("HWND after impersonation " + str(hwnd))
        # ps_list = win32ts.WTSEnumerateProcesses(svr, 1, 0)
        # for ps in ps_list:
        #    logging.info("PS " + str(ps))
        win32ts.WTSCloseServer(svr)

        # Revert back to normal user
        win32security.RevertToSelf()
        user_token.close()


        return

    def grabScreenShot(self):
        # Grab the screen shot and save it to the logs folder
        # Get the hwnd for the current desktop window
        try:
            hwnd = win32gui.GetDesktopWindow()
            #hwnd = self.getDesktopHWND()
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            w = r - l
            h = b - t
            logging.info("SC - HWND " + str(hwnd) + " " + str(w) + "/" + str(h))
            
            dc = win32gui.GetDC(win32con.HWND_DESKTOP)
            logging.info("DC " + str(dc))
            
            dcObj = win32ui.CreateDCFromHandle(dc)
            drawDC = dcObj.CreateCompatibleDC()
            logging.info("drawDC " + str(drawDC))
            
            #cDC = dcObj.CreateCompatibleDC() # Do we need this since it is the desktop dc?
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
            #win32gui.DeleteObject(bm.GetHandle())
        except Exception as ex:
            logging.info("Error grabbing screenshot: " + str(ex))
        
        #m = ImageGrab.grab()

        # Save the file
        #p = os.path.join(SCREEN_SHOTS_FOLDER, str(datetime.datetime.now()) + ".png")
        #im.save(p, optimize=True)
        
        
    def main(self):
        #f = open('D:\\test.txt', 'a')
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            # TODO

            # Grab screen shots
            i = random.randint(0, 2)
            if i == 1:
                #self.grabScreenShot()
                self.runScreenShotApp()
            

            # Grab event logs

            # Grab firewall logs

            # Run virus scanner

            # Security checks - is current user the correct user?

            # Is online?


            #block for 24*60*60 seconds and wait for a stop event
            #it is used for a one-day loop
            rest = 5 * 1000 # 24*60*60*1000
            rc = win32event.WaitForSingleObject(self.hWaitStop, rest)
        
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(OPEService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(OPEService)
