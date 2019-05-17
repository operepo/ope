from __future__ import print_function

import os
import sys
import getpass
import urllib3
urllib3.disable_warnings()
import requests
import ssl
import json
import base64
import pywintypes
import win32api
import win32con
import win32netcon
import ntsecuritycon
import win32security
import win32net
import ctypes
import pythoncom
from win32com.shell import shell, shellcon
import time

# import _winreg as winreg
# from winregistry import winregistry as winreg
######### NOTE - Modified winsys to allow 32/64 bit registry views
# We use KEY_WOW64_64KEY to make sure we are in 64 bit view same as LMS app
import winsys
from winsys import accounts, registry, security

import term
from term import p

import win_util

ssl._create_default_https_context = ssl._create_unverified_context

admin_user = "admin"
admin_pass = ""
smc_url = "https://smc.ed"
student_user = ""

server_name = None
home_root = "c:\\users"
APP_FOLDER = None

def get_app_folder():
    global APP_FOLDER
    ret = ""
    # Adjusted to save APP_FOLDER - issue #6 - app_folder not returning the same folder later in the app?
    if APP_FOLDER is None:
        # return the folder this app is running in.
        # Logger.info("Application: get_app_folder called...")
        if getattr(sys, 'frozen', False):
            # Running in pyinstaller bundle
            ret = sys._MEIPASS
            # Logger.info("Application: sys._MEIPASS " + sys._MEIPASS)
            # Adjust to use sys.executable to deal with issue #6 - path different if cwd done
            # ret = os.path.dirname(sys.executable)
            # Logger.info("AppPath: sys.executable " + ret)

        else:
            ret = os.path.dirname(os.path.abspath(__file__))
            # Logger.info("AppPath: __file__ " + ret)
        APP_FOLDER = ret
    else:
        ret = APP_FOLDER
    return ret


# Make sure the app knows where its folder is at
get_app_folder()


def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        # We are admin, run the main function
        main()
    else:

        print(sys.executable + " " + sys.argv[0])
        hinstance = ctypes.windll.shell32.ShellExecuteW(
            None, u'runas', "c:/Python27/python.exe", sys.argv[0].encode('utf-8'), None, SW.SHOWNORMAL
        )
        if hinstance <= 32:
            raise RuntimeError(ERROR(hinstance))


def print_app_header():
    # Print the header for the app

    txt = """
    
        
}}mn======================================================================
}}mn| }}ybOPE Credential App                                                 }}mn|
}}mn| }}xxThis app will add student credentials to the computer and          }}mn|
}}mn| }}xxsecure the laptop for inmate use.                                  }}mn|
}}mn======================================================================}}xx

    """

    p(txt)


def print_checklist_warning():
    # Print a warning reminding IT staff to properly secure the laptop in the Bios

    txt = """
}}mn======================================================================
}}mn| }}rbWARNING!!! }}xxEnsure that the boot from USB or boot from SD card        }}mn|
}}mn| }}xxoptions in the bios are disabled and that the admin password is    }}mn|
}}mn| }}xxset to a strong random password.                                   }}mn|
}}mn======================================================================}}xx
    """

    p(txt)

    
def verify_ope_account_in_smc(user_name, smc_url, admin_user, admin_pw):
    # Bounce off the SMC server to see if the student account exists in SMC
    # NOTE - this one does NOT check canvas for the user
    
    laptop_admin_user = ""
    laptop_admin_password = ""
    student_full_name = ""
    
    
    api_url = smc_url
    if not api_url.endswith("/"):
        api_url += "/"

    # Need to use basic auth for this
    key = base64.b64encode(admin_user + ':' + admin_pass)
    headers = {'Authorization': 'Basic ' + key}

    p("\n}}gnChecking user status in SMC tool...}}xx\n")
    url = api_url + "lms/verify_ope_account_in_smc.json/" + student_user

    try:
        resp = requests.get(url, headers=headers, verify=False)  # urllib3.Get(url, None, headers)
    except requests.ConnectionError as error_message:
        p("}}rbConnection error trying to connect to SMC server}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return None
        
    if resp is None:
        # Unable to get a response?
        p("}}rbInvalid response from SMC server!}}xx")
        return None
    
    if resp.status_code == requests.codes.forbidden:
        p("}}rbError authenticating with SMC server - check password and try again.}}xx")
        return None
    
    try:
        resp.raise_for_status()
    except Exception as error_message:
        p("}}rbGeneral error trying to connect to SMC server}}xx")
        p("}}ybApplyingMake sure SMC is fully up to date}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return None
        
    smc_response = None
    try:
        smc_response = resp.json()
    except ValueError as error_message:
        p("}}rbInvalid JSON reponse from SMC}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return None
    except Exception as error_message:
        p("}}rbUNKNOWN ERROR}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return None
    
    # Interpret response from SMC
    try:
        msg = smc_response["msg"]
        if msg == "Invalid User!":
            p("\n}}rbInvalid User!}}xx")
            p("}}mnUser doesn't exit in system, please import this student in the SMC first!}}xx")
            return None
        if msg == "No username specified!":
            p("\n}}rbInvalid User!}}xx")
            p("}}mnNo user with this name exists, please import this student in the SMC first!}}xx")
            return None
        student_full_name = smc_response["student_full_name"]
        laptop_admin_user = smc_response["laptop_admin_user"]
        laptop_admin_password = smc_response["laptop_admin_password"]
    except Exception as error_message:
        p("}}rbUnable to interpret response from SMC - no msg parameter returned}}xx")
        p("}}mn" + str(error_message) + "}}xx")
        # p(str(smc_response))
        return None
    
    return (laptop_admin_user, laptop_admin_password, student_full_name)

    
def main():
    global APP_FOLDER

    if win_util.is_admin() is not True:
        p("}}rbApp must be run as Admin user with elevated (UAC) privileges!!!}}xx")
        return False

    global admin_user, admin_pass, smc_url, student_user, server_name, home_root
    canvas_access_token = ""
    canvas_url = "https://canvas.ed"
    win_util.disable_guest_account()
    
    # win_util.test_reg()
    
    # See if we already have a user credentialed.
    last_student_user = win_util.get_credentialed_student_name(default_value="")
    last_smc_url = win_util.get_last_smc_url(default_value="https://smc.ed")
    last_admin_user = win_util.get_last_admin_user(default_value="admin")

    # p("LAST STUDENT USER: " + str(last_student_user))
    # We want to make sure to disable any accounts that were previously setup
    # don't want more then one student being able to login at a time
    win_util.disable_student_accounts()
    
    print_app_header()
    # Ask for admin user/pass and website
    tmp = raw_input(term.translate_color_codes("}}ynEnter URL for SMC Server }}cn[enter for " + last_smc_url + "]:}}xx "))
    tmp = tmp.strip()
    if tmp == "":
        tmp = last_smc_url
    smc_url = tmp

    tmp = raw_input(term.translate_color_codes("}}ynPlease enter the ADMIN user name }}cn[enter for " + last_admin_user + "]:}}xx "))
    tmp = tmp.strip()
    if tmp == "":
        tmp = last_admin_user
    admin_user = tmp

    p("}}ynPlease enter ADMIN password }}cn[characters will not show]:}}xx", False)
    tmp = getpass.getpass(" ")
    if tmp == "":
        p("}}rbA password is required.}}xx")
        return False
    admin_pass = tmp

    tmp = ""
    last_student_user_prompt = ""
    while tmp.strip() == "":
        if last_student_user != "":
            last_student_user_prompt = " }}cn[enter for previous student " + last_student_user + "]"
            # p("}}mb\t- Found previously credentialed user: }}xx" + str(last_student_user))
        tmp = raw_input(term.translate_color_codes("}}ynPlease enter the username for the student" + last_student_user_prompt + ":}}xx "))
        if tmp.strip() == "":
            tmp = last_student_user
    student_user = tmp.strip()
    
    result = verify_ope_account_in_smc(student_user, smc_url, admin_user, admin_pass)
    if result is None:
        p("}}rbERR - User doesn't exist in smc??}}xx")
        sys.exit(-1)
    laptop_admin_user, laptop_admin_password, student_full_name = result
    
    if laptop_admin_user == "" or laptop_admin_password == "":
        p("}}rbERR - Please set the laptop admin credentials in the SMC before continuing (Admin -> Configure App -> Laptop Admin Credentials) }}xx")
        sys.exit(-1)
    
    if student_full_name == "":
        p("}}rbERR - Unable to find student user in the SMC? Make sure it is imported.}}xx")
        sys.exit(-1)
    
    # Show confirm info
    txt = """
}}mn======================================================================
}}mn| }}ybConfirm Credential Parameters                                      }}mn|
}}mn| }}ynSMC URL:            }}cn<smc_url>}}mn|
}}mn| }}ynAdmin User:         }}cn<admin_user>}}mn|
}}mn| }}ynAdmin Password:     }}cn<admin_pass>}}mn|
}}mn| }}ynStudent Username:   }}cn<student_user>}}mn|
}}mn======================================================================}}xx
    """
    txt = txt.replace("<smc_url>", smc_url.ljust(47))
    txt = txt.replace("<admin_user>", admin_user.ljust(47))
    txt = txt.replace("<admin_pass>", "******".ljust(47))
    student_text = student_user + " (" + student_full_name + ")"
    txt = txt.replace("<student_user>", student_text.ljust(47))

    p(txt)
    tmp = raw_input(term.translate_color_codes("}}ybPress Y to continue: }}xx"))
    tmp = tmp.strip().lower()
    if tmp != "y":
        p("}}cnCanceled / Not credentialing....}}xx")
        return False
    
    api_url = smc_url
    if not api_url.endswith("/"):
        api_url += "/"

    key = base64.b64encode(admin_user + ':' + admin_pass)
    headers = {'Authorization': 'Basic ' + key}

    # password_manager = urllib3.HTTPPasswordMgrWithDefaultRealm()
    # password_manager.add_password(None, api_url, admin_user, admin_pass)
    # handler = urllib3.HTTPBasicAuthHandler(password_manager)
    # opener = urllib3.build_opener(handler)
    # ssl_context = ssl._create_unverified_context()

    p("\n}}gnStarting Credential Process...}}xx\n")
    url = api_url + "lms/credential_student.json/" + student_user
    
    try:
        resp = requests.get(url, headers=headers, verify=False)  # urllib3.Request(url, None, headers)
    except requests.ConnectionError as error_message:
        p("}}rbConnection error trying to connect to SMC server}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return False
    
    if resp is None:
        # Unable to get a response?
        p("}}rbInvalid response from SMC server!}}xx")
        return False
    
    if resp.status_code == requests.codes.forbidden:
        p("}}rbError authenticating with SMC server - check password and try again.}}xx")
        return False
    
    try:
        resp.raise_for_status()
    except Exception as error_message:
        p("}}rbGeneral error trying to connect to SMC server}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return False
    
    smc_response = None
    
    try:
        smc_response = resp.json()
    except ValueError as error_message:
        p("}}rbInvalid JSON response from SMC}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return False
    except Exception as error_message:
        p("}}rbUNKNOWN ERROR}}xx")
        p("}}yn" + str(error_message) + "}}xx")
        return False

    # Interpret response from SMC
    try:
        # p("RESP: " + str(smc_response))
        msg = smc_response["msg"]
        if msg == "Invalid User!":
            p("\n}}rbInvalid User!}}xx")
            p("}}mnUser doesn't exit in system, please import this student in the SMC first!}}xx")
            return False
        if msg == "No username specified!":
            p("\n}}rbInvalid User!}}xx")
            p("}}mnNo user with this name exists, please import this student in the SMC first!}}xx")
            return False
        if "unable to connect to canvas db" in msg:
            p("\n}}rbSMC Unable to connect to Canvas DB - make sure canvas app is running and\n" +
              "the SMC tool is configured to talk to Canvas}}xx")
            p("}}yn" + str(msg) + "}}xx")
            return False
        if "Unable to find user in canvas:" in  msg:
            p("\n}}rbInvalid User!}}xx")
            p("}}mnUser exists in SMC but not in Canvas, please rerun import this student in the SMC to correct the issue!}}xx")
        full_name = smc_response["full_name"]
        canvas_access_token = str(smc_response["key"])
        hash = str(smc_response["hash"])
        student_full_name = str(smc_response["full_name"])
        canvas_url = str(smc_response['canvas_url'])
    except Exception as error_message:
        p("}}rbUnable to interpret response from SMC - no msg parameter returned}}xx")
        p("}}mn" + str(ex) + "}}xx")
        return False
    
    # p("Response: " + canvas_access_token + " ---- " + hash)
    pw = win_util.decrypt(hash, canvas_access_token)

    p("}}gnCreating local student windows account...")
    win_util.create_local_student_account(student_user, student_full_name, pw)
    
    p("}}gnCreating local admin windows account...")
    try:
        win_util.create_local_admin_account(laptop_admin_user, "OPE Laptop Admin", laptop_admin_password)
    except Exception as ex:
        p("}}rbError setting up OPE Laptop Admin Account " + str(ex))
    laptop_admin_password = ""

    # Store the access token in the registry where the LMS app can pick it up
    p("}}gn\nSaving canvas credentials for student...")
    # key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS", student_user)
    # key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS\student")
    # key.canvas_access_token = canvas_access_token
    # key.user_name = student_user
    win_util.set_registry_value('canvas_access_token', canvas_access_token)
    win_util.set_registry_value('user_name', student_user)
    win_util.set_registry_value('canvas_url', canvas_url)
    win_util.set_registry_value('smc_url', smc_url)
    win_util.set_registry_value('admin_user', admin_user)
    win_util.set_registry_permissions(student_user)
    
    # p("}}gnCanvas access granted for student.}}xx")

    p("\n}}gnSetting up LMS App...}}xx")
    # Create shortcut
    lnk_path = "c:\\users\\public\\desktop\\OPE LMS.lnk"

    # Modify so that desktop shortcut point to where the app really is, not the hard coded dir
    # exe_path = "c:\\programdata\\ope\\ope_laptop_binaries\\lms\\ope_lms.exe"
    LMS_FOLDER = os.path.join(os.path.dirname(APP_FOLDER), "lms")
    exe_path = os.path.join(LMS_FOLDER, "ope_lms.exe")
    # ico_path = "c:\\programdata\\ope\\ope_laptop_binaries\\lms\\logo_icon.ico"
    ico_path = os.path.join(LMS_FOLDER, "logo_icon.ico")
    shortcut = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_IShellLink
    )
    shortcut.SetPath(exe_path)
    shortcut.SetDescription("Offline LMS app for Open Prison Education project")
    shortcut.SetIconLocation(ico_path, 0)
    persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Save(lnk_path, 0)

    # If current user is not the laptop_admin_user - ask if we should disable this account?
    me = accounts.me()
    if laptop_admin_user != me.name:
        p("}}rb!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        p("}}rbYou are currently logged in as " + str(me.name) + " but the Laptop Admin user is " + str(laptop_admin_user) + ".")
        p("}}rb---> Please make sure to set a password and/or disable accounts that aren't needed on this laptop.}}xx")
        p("}}rb!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        countdown = 8
        while countdown > 0:
            p("\r}}mb" + str(countdown) + "}}xx", end="")
            time.sleep(1)
            countdown -= 1
    p("\n}}gbCanvas token saved.}}xx")
    p("")
    p("}}zn            -------------->                 !!!!!CONFIRM BIOS!!!!!                   <--------------                   }}xx")
    p("}}zn            --------------> VERIFY BIOS PASSWORD/SETTINGS BEFORE HANDING OUT LAPTOP! <--------------                   }}xx")

    countdown = 8
    while countdown > 0:
        p("\r}}mb" + str(countdown) + "}}xx", end="")
        time.sleep(1)
        countdown -= 1

    return True
    
    
def scratch():
    
    # print("Installing Admin Services...")

    # print("Installing offline LMS app...")

    # print ("Applying security rules...")

    p("\tDownloading firewall rules...")
    url = api_url + "lms/get_firewall_list.json"
    p("\n\nURL: " + url)

    request = urllib3.Request(url, None, headers)
    json_str = ""
    try:
        response = urllib3.urlopen(request)
        json_str = response.read()
    except urllib3.HTTPError as ex:
        if ex.code == 403:
            p("}}rbInvalid ADMIN Password!}}xx")
            return False
        else:
            p("}}rbHTTP Error!}}xx")
            p("}}mn" + str(ex) + "}}xx")
            return False
    except Exception as ex:
        p("}}rbUnable to communicate with SMC tool!}}xx")
        p("}}mn" + str(ex) + "}}xx")
        return False

    firewall_response = None
    try:
        firewall_response = json.loads(json_str)
    except Exception as ex:
        p("}}rbUnable to interpret firewall response from SMC}}xx")
        p("}}mn" + str(ex) + "}}xx")
        return False

    for rule in firewall_response:
        p("}}ybApplying Firewall Rule: " + str(rule["rule_name"]))
        fw_cmd = "netsh advfirewall firewall delete rule \"" + str(rule["rule_name"]) + "\""
        p("\t\t}}rn" + fw_cmd)
        os.system(fw_cmd)
        fw_cmd = "netsh advfirewall firewall add rule name=\"" + str(rule["rule_name"]) + "\""
        if rule["protocol"] != "":
            fw_cmd += " protocol="+rule["protocol"]
        if rule["rmtusrgrp"] != "":
            fw_cmd += " rmtusrgrp=" + rule["rmtusrgrp"]
        if rule["rmtcomputergrp"] != "":
            fw_cmd += " rmtcomputergrp=" + rule["rmtcomputergrp"]
        if rule["description"] != "":
            fw_cmd += " description=\"" + rule["description"].replace("\"", "") + "\""
        if rule["service"] != "":
            fw_cmd += " service=\"" + rule["service"] + "\""
        if rule["fw_action"] != "":
            fw_cmd += " action=" + rule["fw_action"]
        if rule["fw_security"] != "":
            fw_cmd += " security=" + rule["fw_security"]
        if rule["program"] != "":
            fw_cmd += " program=\"" + rule["program"].replace("\"", "") + "\""
        if rule["profile"] != "":
            fw_cmd += " profile=" + rule["profile"]
        if rule["direction"] != "":
            fw_cmd += " direction=" + rule["direction"]
        if rule["remoteip"] != "":
            fw_cmd += " remoteip=" + rule["remoteip"]
        if rule["fw_enable"] != "":
            fw_cmd += " enable=" + rule["fw_enable"]
        if rule["remoteport"] != "":
            fw_cmd += " remoteport=" + rule["remoteport"]
        if rule["localport"] != "":
            fw_cmd += " localport=" + rule["localport"]
        if rule["localip"] != "":
            fw_cmd += " localip=" + rule["localip"]
        if rule["edge"] != "":
            fw_cmd += " edge=" + rule["edge"]
        if rule["interfacetype"] != "":
            fw_cmd += " interfacetype=" + rule["interfacetype"]
        p("\t\t}}rb" + fw_cmd)
        os.system(fw_cmd)

    # Turn the firewall on
    # netsh advfirewall set allprofiles state on
    # Default Settings
    # netsh advfirewall reset
    # Set logging
    # netsh advfirewall set currentprofile logging filename "C:\temp\pfirewall.log"
    # Block ping
    # netsh advfirewall firewall add rule name="All ICMP V4" dir=in action=block protocol=icmpv4
    # Allow ping
    # netsh advfirewall firewall add rule name="All ICMP V4" dir=in action=allow protocol=icmpv4
    # Allow or deny port
    # netsh advfirewall firewall add rule name="Open SQL Server Port 1433" dir=in action=allow protocol=TCP localport=1433
    # netsh advfirewall firewall delete rule name="Open SQL Server Port 1433" protocol=tcp localport=1433
    # Enable program
    # netsh advfirewall firewall add rule name="Allow Messenger" dir=in action=allow program="C:\programfiles\messenger\msnmsgr.exe"
    # Enable remote manatement
    # netsh advfirewall firewall set rule group="remote administration" new enable=yes
    # Enable remote desktop
    # netsh advfirewall firewall set rule group="remote desktop" new enable=Yes
    # Export settings
    # netsh advfirewall export "C:\temp\WFconfiguration.wfw"

    # Get repo over test cert
    # git -c http.sslVerify=false clone https://example.com/path/to/git

    # TODO
    # Download current policy zip file
    # unzip
    # import
    # /mergedpolicy -- to combine domain/local
    cmd = "cd policy_dir; secedit /export /cfg gp.ini /log export.log"

    # netsh -- import firewall rules
    # download netsh import
    # run netsh import command

    print_checklist_warning()

    a = raw_input(term.translate_color_codes("}}ybPress enter when done}}xx"))

    return True


def deviceDetection():
    import wmi

    local_machine = wmi.WMI()
    for os in local_machine.Win32_OperatingSystem():
        p(os.Caption)

    #disk_watcher = local_machine.
    p(local_machine.methods.keys())


def listUSB():
    import usb
    import usb.core
    import usb.util

    #busses = usb.busses()
    #for bus in busses:
    #    devices = bus.devices
    #    for dev in devices:
    #        print "Device: ", dev

    devices = usb.core.find(find_all=True)
    #n = devices.next()
    #print n
    for dev in devices:
        d_class = dev.bDeviceClass
        p("Device Found: " + str(dev.bcdDevice))
        try:
            p(dev)
        except:
            pass

def listNics():
    system_nics = ["WAN Miniport (IP)", "WAN Miniport (IPv6)", "WAN Miniport (Network Monitor)",
        "WAN Miniport (PPPOE)", "WAN Miniport (PPTP)", "WAN Miniport (L2TP)", "WAN Miniport (IKEv2)",
        "WAN Miniport (SSTP)", "Microsoft Wi-Fi Direct Virtual Adapter", "Teredo Tunneling Pseudo-Interface",
        "Microsoft Kernel Debug Network Adapter",
        ]
    approved_nics = ["Realtek USB GbE Family Controller",]

    import win32com.client
    strComputer = "."
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_NetworkAdapter")
    for objItem in colItems:
        if objItem.Name in approved_nics:
            p("***Device found - on approved list: ", objItem.Name, str(objItem.NetConnectionID))
            continue
        elif objItem.Name in system_nics:
            #p("***Device found - system nic - ignoring: ", objItem.Name)
            continue
        else:
            p("***Device found :", objItem.Name)
            dev_id = objItem.NetConnectionID
            if dev_id:
                p("     ---> !!! unauthorized !!!, disabling...", str(dev_id))
                cmd = "netsh interface set interface \"" + dev_id + "\" DISABLED"
                #print cmd
                os.system(cmd)
            else:
                #p("     ---> unauthorized, not plugged in...")
                pass
            continue
           
        p("========================================================")
        p("Adapter Type: ", objItem.AdapterType)
        p("Adapter Type Id: ", objItem.AdapterTypeId)
        p("AutoSense: ", objItem.AutoSense)
        p("Availability: ", objItem.Availability)
        p("Caption: ", objItem.Caption)
        p("Config Manager Error Code: ", objItem.ConfigManagerErrorCode)
        p("Config Manager User Config: ", objItem.ConfigManagerUserConfig)
        p("Creation Class Name: ", objItem.CreationClassName)
        p("Description: ", objItem.Description)
        p("Device ID: ", objItem.DeviceID)
        #p("Error Cleared: ", objItem.ErrorCleared)
        #p("Error Description: ", objItem.ErrorDescription)
        #p("Index: ", objItem.Index)
        #p("Install Date: ", objItem.InstallDate)
        #p("Installed: ", objItem.Installed)
        #p("Last Error Code: ", objItem.LastErrorCode)
        #p("MAC Address: ", objItem.MACAddress)
        p("Manufacturer: ", objItem.Manufacturer)
        #p("Max Number Controlled: ", objItem.MaxNumberControlled)
        #p("Max Speed: ", objItem.MaxSpeed)
        p("Name: ", objItem.Name)
        p("Net Connection ID: ", objItem.NetConnectionID)
        p("Net Connection Status: ", objItem.NetConnectionStatus)
        z = objItem.NetworkAddresses
        if z is None:
            a = 1
        else:
            for x in z:
                p("Network Addresses: ", x)
        #print "Permanent Address: ", objItem.PermanentAddress
        p("PNP Device ID: ", objItem.PNPDeviceID)
        #z = objItem.PowerManagementCapabilities
        #if z is None:
        #    a = 1
        #else:
        #    for x in z:
        #        p("Power Management Capabilities: ", x)
        #p("Power Management Supported: ", objItem.PowerManagementSupported)
        p("Product Name: ", objItem.ProductName)
        p("Service Name: ", objItem.ServiceName)
        #p("Speed: ", objItem.Speed)
        #p("Status: ", objItem.Status)
        #p("Status Info: ", objItem.StatusInfo)
        p("System Creation Class Name: ", objItem.SystemCreationClassName)
        p("System Name: ", objItem.SystemName)
        #p("Time Of Last Reset: ", objItem.TimeOfLastReset)


if __name__ == "__main__":
    # TODO Make sure this runs as admin
    #
    if not main():
        # Make sure to return error code so it can be caught at next level
        sys.exit(1)

    #deviceDetection()
    #listUSB()
    #listNics()
    sys.exit(0)
