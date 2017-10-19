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

LOG_FOLDER = os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
SCREEN_SHOTS_FOLDER = os.path.join(LOG_FOLDER, "screen_shots")
print LOG_FOLDER

# Setup loggin
logging.basicConfig(
    filename = os.path.join(LOG_FOLDER, 'ope-service-test.log'),
    level = logging.DEBUG,
    format = '[ope-service] %(levelname)-7.7s %(message)s'
)


# Get SID for everyone, admin groups and current user
EVERYONE, domain, type = win32security.LookupAccountName("", "Everyone")
ADMINISTRATORS, domain, type = win32security.LookupAccountName("", "Administrators")
CURRENT_USER, domain, type = win32security.LookupAccountName("", win32api.GetUserName())
SYSTEM_USER, domain, type = win32security.LookupAccountName("", "System")

def show_cacls(filename):
    print
    print
    for line in os.popen("cacls %s" % filename).read().splitlines():
        print line

def make_data_folder(folder):
    try:
        os.makedirs(folder)
    except:
        pass
        
    # Set permissions on this folder so that it isn't viewable by students
    sd = win32security.GetFileSecurity(folder, win32security.DACL_SECURITY_INFORMATION)
    
    # Create the blank DACL and add our ACE's
    dacl = win32security.ACL()
    #dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_GENERIC_READ, EVERYONE)
    #dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_WRITE, CURRENT_USER)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_ALL_ACCESS, ADMINISTRATORS)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_ALL_ACCESS, SYSTEM_USER)
    
    # Set our ACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(folder, win32security.DACL_SECURITY_INFORMATION, sd)
    
def grabScreenShot():
    # Grab the screen shot and save it to the logs folder
    # Get the hwnd for the current desktop window
    try:

        #hwnd = win32gui.GetDesktopWindow()
        hwnd = getDesktopWindow()
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
    
        

def getDesktopWindow():
    console_id = win32ts.WTSGetActiveConsoleSessionId()
    if console_id == 0xffffffff:
        # User not logged in right now?
        logging.info("No console user")
        return None

    hwnd = None

    # Get processes running on this console
    svr = win32ts.WTSOpenServer(".")
    ps_list = win32ts.WTSEnumerateProcesses(svr, 1, 0)
    for ps in ps_list:
        logging.info("PS " + str(ps))
    win32ts.WTSCloseServer(svr)
    # sessions = win32ts.WTSEnumerateSessions(None, 1, 0)
    # for session in win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE, 1, 0):
    #         print "SessionId: %s" % session['SessionId']
    #         print "\tWinStationName: %s" % session['WinStationName']
    #         print "\tState: %s" % session['State']
    #         print
    #         if session["WinStationName"] == "Console":
    #             cs = session

    #if cs is not None:
    #    # Get process list for this session
    return hwnd
    
#cs = getDesktopWindow()
grabScreenShot()
#print cs

# Make the folders
#make_data_folder(LOG_FOLDER)
#make_data_folder(SCREEN_SHOTS_FOLDER)



# Clear current permissions, inheritance, and add system/admins back on

# Setup entries
# entries = [{'AccessMode': win32security.GRANT_ACCESS,
            # 'AccessPermissions': 0,
            # 'Inheritance': win32security.CONTAINER_INHERIT_ACE |
                           # win32security.OBJECT_INHERIT_ACE,
            # 'Trustee': {'TrusteeType': win32security.TRUSTEE_IS_USER,
                        # 'TrusteeForm': win32security.TRUSTEE_IS_NAME,
                        # 'Identifier': ''}}
            # for i in range(2)]

#Add our entries
# entries[0]['AccessPermissions'] = (ntsecuritycon.GENERIC_READ |
                                   # ntsecuritycon.GENERIC_WRITE)
# entries[0]['Trustee']['Identifier'] = USERX
# entries[1]['AccessPermissions'] = ntsecuritycon.GENERIC_ALL
# entries[1]['Trustee']['Identifier'] = "Administrators"


#HDC desktopDC = GetDC( HWND_DESKTOP ) ;

#// or
#HDC desktopDC2 = GetDC( NULL ) ;

#// or
#HDC desktopDC3 = GetDC( 0 ) ;

#// same diff

#// don't forget to
#ReleaseDC( HWND_DESKTOP, desktopDC ) ;
#// when you're done!
