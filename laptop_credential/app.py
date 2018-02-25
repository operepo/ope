import os
import sys
import getpass
import urllib2
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

import _winreg as winreg
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
    # Print a the header for the app

    txt = """
}}mn======================================================================
}}mn| }}ybOPE Credential App                                                 }}mn|
}}mn| }}dnThis app will add student credentials to the computer and          }}mn|
}}mn| }}dnsecure the laptop for inmate use.                                  }}mn|
}}mn======================================================================}}dn

    """

    p(txt)


def print_checklist_warning():
    # Print a warning reminding IT staff to properly secure the laptop in the Bios

    txt = """
}}mn======================================================================
}}mn| }}rbWARNING!!! }}dnEnsure that the boot from USB or boot from SD card        }}mn|
}}mn| }}dnoptions in the bios are disabled and that the admin password is    }}mn|
}}mn| }}dnset to a strong random password.                                   }}mn|
}}mn======================================================================}}dn
    """

    p(txt)


def main():
    global admin_user, admin_pass, smc_url, student_user, server_name, home_root
    canvas_access_token = ""

    print_app_header()
    # Ask for admnin user/pass and website
    tmp = raw_input(term.translateColorCodes("}}ynEnter URL for SMC Server }}cn[enter for default " + smc_url + "]:}}dn "))
    tmp = tmp.strip()
    if tmp == "":
        tmp = smc_url
    smc_url = tmp

    tmp = raw_input(term.translateColorCodes("}}ynPlease enter the ADMIN user name }}cn[enter for default " + admin_user + "]:}}dn "))
    tmp = tmp.strip()
    if tmp == "":
        tmp = admin_user
    admin_user = tmp

    p("}}ynPlease enter ADMIN password }}cn[characters will not show]:}}dn", False)
    tmp = getpass.getpass(" ")
    if tmp == "":
        p("}}rbA password is required.}}dn")
        return False
    admin_pass = tmp

    tmp = ""
    while tmp.strip() == "":
        tmp = raw_input(term.translateColorCodes("}}ynPlease enter the username for the student:}}dn "))
    student_user = tmp.strip()

    txt = """
}}mn======================================================================
}}mn| }}ybCredential Computer                                                }}mn|
}}mn| }}ynSMC URL:            }}cn<smc_url>}}mn|
}}mn| }}ynAdmin User:         }}cn<admin_user>}}mn|
}}mn| }}ynAdmin Password:     }}cn<admin_pass>}}mn|
}}mn| }}ynStudent Username:   }}cn<student_user>}}mn|
}}mn======================================================================}}dn
    """
    txt = txt.replace("<smc_url>", smc_url.ljust(47))
    txt = txt.replace("<admin_user>", admin_user.ljust(47))
    txt = txt.replace("<admin_pass>", "******".ljust(47))
    txt = txt.replace("<student_user>", student_user.ljust(47))

    p(txt)
    tmp = raw_input(term.translateColorCodes("}}ybPress Y to continue: }}dn"))
    tmp = tmp.strip().lower()
    if tmp == "y":
        api_url = smc_url
        if not api_url.endswith("/"):
            api_url += "/"

        key = base64.b64encode(admin_user + ':' + admin_pass)
        headers = {'Authorization': 'Basic ' + key}

        # password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # password_manager.add_password(None, api_url, admin_user, admin_pass)
        # handler = urllib2.HTTPBasicAuthHandler(password_manager)
        # opener = urllib2.build_opener(handler)
        # ssl_context = ssl._create_unverified_context()

        p("\n}}gnGetting Canvas Auth Key...}}dn\n")
        url = api_url + "lms/credential_student.json/" + student_user

        request = urllib2.Request(url, None, headers)
        json_str = ""
        try:
            response = urllib2.urlopen(request)
            json_str = response.read()
        except urllib2.HTTPError as ex:
            if ex.code == 403:
                p("}}rbInvalid ADMIN Password!}}dn")
                return False
            else:
                p("}}rbHTTP Error!}}dn")
                p("}}mn" + str(ex) + "}}dn")
                return False
        except Exception as ex:
            p("}}rbUnable to communicate with SMC tool!}}dn")
            p("}}mn" + str(ex) + "}}dn")
            return False

        canvas_response = None
        try:
            canvas_response = json.loads(json_str)
        except Exception as ex:
            p("}}rbUnable to interpret response from SMC}}dn")
            p("}}mn" + str(ex) + "}}dn")
            return False
        if "msg" in canvas_response:
            if canvas_response["msg"] == "Invalid User!":
                p("\n}}rbInvalid User!}}dn")
                p("}}mnUser doesn't exit in system, please import this student in the SMC first!}}dn")
                return False
            if "Unable to find user in canvas:" in  canvas_response["msg"]:
                p("\n}}rbInvalid User!}}dn")
                p("}}mnUser exists in SMC but not in Canvas, please rerun import this student in the SMC to correct the issue!}}dn")
                return False

        canvas_access_token = str(canvas_response["key"])
        hash = str(canvas_response["hash"])
        student_full_name = str(canvas_response["full_name"])

        # print("Response: " + canvas_access_token + " ---- " + hash)
        pw = win_util.decrypt(hash, canvas_access_token)

        p("}}gnCreating local windows account...")
        win_util.create_local_student_account(student_user, student_full_name, pw)

        # Store the access token in the registry where the LMS app can pick it up
        p("}}gnSaving canvas credentials for student...")
        key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS", student_user)
        key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS\student")
        key.canvas_access_token = canvas_access_token
        
        print("Canvas access granted for student.")

        print("Setting up LMS App...")
        # Create shortcut
        lnk_path = "c:\\users\\public\\desktop\\OPE LMS.lnk"
        exe_path = "c:\\programdata\\ope\\ope_laptop_binaries\\lms\\ope_lms.exe"
        ico_path = "c:\\programdata\\ope\\ope_laptop_binaries\\lms\\logo_icon.ico"
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

        return True

        # print("Installing Admin Services...")

        # print("Installing offline LMS app...")

        # print ("Applying security rules...")

        p("\tDownloading firewall rules...")
        url = api_url + "lms/get_firewall_list.json"
        p("\n\nURL: " + url)

        request = urllib2.Request(url, None, headers)
        json_str = ""
        try:
            response = urllib2.urlopen(request)
            json_str = response.read()
        except urllib2.HTTPError as ex:
            if ex.code == 403:
                p("}}rbInvalid ADMIN Password!}}dn")
                return False
            else:
                p("}}rbHTTP Error!}}dn")
                p("}}mn" + str(ex) + "}}dn")
                return False
        except Exception as ex:
            p("}}rbUnable to communicate with SMC tool!}}dn")
            p("}}mn" + str(ex) + "}}dn")
            return False

        firewall_response = None
        try:
            firewall_response = json.loads(json_str)
        except Exception as ex:
            p("}}rbUnable to interpret firewall response from SMC}}dn")
            p("}}mn" + str(ex) + "}}dn")
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

        a = raw_input(term.translateColorCodes("}}ybPress enter when done}}dn"))

        return True


def deviceDetection():
    import wmi

    local_machine = wmi.WMI()
    for os in local_machine.Win32_OperatingSystem():
        print os.Caption

    #disk_watcher = local_machine.
    print local_machine.methods.keys()


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
        print "Device Found: " + str(dev.bcdDevice)
        try:
            print dev
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
            print "***Device found - on approved list: ", objItem.Name, str(objItem.NetConnectionID)
            continue
        elif objItem.Name in system_nics:
            #print "***Device found - system nic - ignoring: ", objItem.Name
            continue
        else:
            print "***Device found :", objItem.Name
            dev_id = objItem.NetConnectionID
            if dev_id:
                print "     ---> !!! unauthorized !!!, disabling...", str(dev_id)
                cmd = "netsh interface set interface \"" + dev_id + "\" DISABLED"
                #print cmd
                os.system(cmd)
            else:
                #print "     ---> unauthorized, not plugged in..."
                pass
            continue
		   
        print "========================================================"
        print "Adapter Type: ", objItem.AdapterType
        print "Adapter Type Id: ", objItem.AdapterTypeId
        print "AutoSense: ", objItem.AutoSense
        print "Availability: ", objItem.Availability
        print "Caption: ", objItem.Caption
        print "Config Manager Error Code: ", objItem.ConfigManagerErrorCode
        print "Config Manager User Config: ", objItem.ConfigManagerUserConfig
        print "Creation Class Name: ", objItem.CreationClassName
        print "Description: ", objItem.Description
        print "Device ID: ", objItem.DeviceID
        #print "Error Cleared: ", objItem.ErrorCleared
        #print "Error Description: ", objItem.ErrorDescription
        #print "Index: ", objItem.Index
        #print "Install Date: ", objItem.InstallDate
        #print "Installed: ", objItem.Installed
        #print "Last Error Code: ", objItem.LastErrorCode
        #print "MAC Address: ", objItem.MACAddress
        print "Manufacturer: ", objItem.Manufacturer
        #print "Max Number Controlled: ", objItem.MaxNumberControlled
        #print "Max Speed: ", objItem.MaxSpeed
        print "Name: ", objItem.Name
        print "Net Connection ID: ", objItem.NetConnectionID
        print "Net Connection Status: ", objItem.NetConnectionStatus
        z = objItem.NetworkAddresses
        if z is None:
            a = 1
        else:
            for x in z:
                print "Network Addresses: ", x
        #print "Permanent Address: ", objItem.PermanentAddress
        print "PNP Device ID: ", objItem.PNPDeviceID
        #z = objItem.PowerManagementCapabilities
        #if z is None:
        #    a = 1
        #else:
        #    for x in z:
        #        print "Power Management Capabilities: ", x
        #print "Power Management Supported: ", objItem.PowerManagementSupported
        print "Product Name: ", objItem.ProductName
        print "Service Name: ", objItem.ServiceName
        #print "Speed: ", objItem.Speed
        #print "Status: ", objItem.Status
        #print "Status Info: ", objItem.StatusInfo
        print "System Creation Class Name: ", objItem.SystemCreationClassName
        print "System Name: ", objItem.SystemName
        #print "Time Of Last Reset: ", objItem.TimeOfLastReset


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
