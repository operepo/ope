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

# Setup loggin
logging.basicConfig(
    filename = os.path.join(LOG_FOLDER, 'ope-service-test.log'),
    level = logging.DEBUG,
    format = '[ope-service] %(levelname)-7.7s %(message)s'
)



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
#grabScreenShot()
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


set_ope_permissions()

