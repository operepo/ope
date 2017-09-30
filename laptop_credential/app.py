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

        canvas_access_token = str(canvas_response["key"])
        hash = str(canvas_response["hash"])
        student_full_name = str(canvas_response["full_name"])

        #print("Response: " + canvas_access_token + " ---- " + hash)
        pw = win_util.decrypt(hash, canvas_access_token)

        p("}}gnCreating local windows account...")
        win_util.create_local_student_account(student_user, student_full_name, pw)


        # Store the access token in the registry where the LMS app can pick it up
        p("}}gnSaving canvas credentials for student...")
        key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS", student_user)
        key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS\student")
        key.canvas_access_token = canvas_access_token

        print("Installing Admin Services...")

        print("Installing offline LMS app...")

        print ("Applying security rules...")

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


if __name__ == "__main__":
    # Make sure this runs as admin
    run_as_admin()


# import win32api
# import win32security
# import _winreg
#
# class Ace(object):
#     ace_flags = {win32security.CONTAINER_INHERIT_ACE: 'Container Inherit',
#                  win32security.FAILED_ACCESS_ACE_FLAG: 'Failed Access',
#                  win32security.INHERIT_ONLY_ACE: 'Inherit only',
#                  win32security.INHERITED_ACE: 'Inherited ACE',
#                  win32security.NO_PROPAGATE_INHERIT_ACE: 'No propagate',
#                  win32security.OBJECT_INHERIT_ACE: 'Object inherit',
#                  win32security.SUCCESSFUL_ACCESS_ACE_FLAG: 'Successful access'}
#
#     def __init__(self, ace):
#         self.ace = ace
#         ( (self.access_type, self.flags), self.mask, self.pysid) = ace
#
#     def getType(self):
#         if self.access_type == win32security.ACCESS_ALLOWED_ACE_TYPE:
#             return "Allow"
#         if self.access_type == win32security.ACCESS_DENIED_ACE_TYPE:
#             return "Deny"
#
#     def getFlags(self):
#         readable_flags = list()
#         for (f, v) in self.ace_flags.items():
#             if f & self.flags == f:
#                 readable_flags.append(v)
#         return readable_flags
#
# class RegKey(object):
#
#     registry_rights = {_winreg.KEY_ALL_ACCESS: 'All Access',
#                       _winreg.KEY_WRITE: 'Write',
#                       _winreg.KEY_READ: 'Read',
#                       _winreg.KEY_EXECUTE: 'Read',
#                       _winreg.KEY_QUERY_VALUE: 'Query value',
#                       _winreg.KEY_SET_VALUE: 'Set value',
#                       _winreg.KEY_CREATE_SUB_KEY: 'Create subkey',
#                       _winreg.KEY_ENUMERATE_SUB_KEYS: 'Enum subkeys',
#                       _winreg.KEY_NOTIFY: 'Request notification',
#                       _winreg.KEY_CREATE_LINK: 'Link (reserved)' }
#
#     def __init__(self, key_path, machine=None, root=_winreg.HKEY_LOCAL_MACHINE):
#         self.registry = _winreg.ConnectRegistry(None, root)
#         self.key_path = key_path
#         self.key = _winreg.OpenKey(self.registry, key_path)
#         self.security = win32api.RegGetKeySecurity(self.key.handle, win32security.DACL_SECURITY_INFORMATION)
#         self.dacl = self.security.GetSecurityDescriptorDacl()
#         self.aces = list()
#         for i in range(self.dacl.GetAceCount()):
#             self.aces.append(Ace(self.dacl.GetAce(i)))
#
#     def dump_values(self):
#         (subkey_count, value_count, last_modified) = _winreg.QueryInfoKey(self.key)
#         print "Values:"
#         for i in range(value_count):
#             (name, data, value_type) = _winreg.EnumValue(self.key, i)
#             print "\t{0}: {1}".format(name, data)
#
#     def dump_subkeys(self):
#         (subkey_count, value_count, last_modified) = _winreg.QueryInfoKey(self.key)
#         print "Subkeys:"
#         for i in range(subkey_count):
#            print "\t{0}".format(_winreg.EnumKey(self.key, i))
#
#     def dump_ace(self, ace):
#         print "Ace: {0}".format(ace.ace)
#         print " Type: {0}".format(ace.getType())
#         print " Flags: {0}".format(", ".join(ace.getFlags()))
#         account = win32security.LookupAccountSid(None, ace.pysid);
#         print " Account: {0}\{1}".format(account[1], account[0])
#         print " Access:"
#         if ace.mask & _winreg.KEY_ALL_ACCESS == _winreg.KEY_ALL_ACCESS:
#             print "\t{0}".format(self.registry_rights[_winreg.KEY_ALL_ACCESS])
#         else:
#             for (p, v) in self.registry_rights.items():
#                 if p & ace.mask == p:
#                    print "\t{0}".format(v)
#
#     def dump_dacl(self):
#         for ace in self.aces:
#             self.dump_ace(ace)
#             print
#
#
# if __name__ == '__main__':
#     r = RegKey(r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
#                root=_winreg.HKEY_CURRENT_USER)
#     r.dump_subkeys()
#     r.dump_values()
#     r.dump_dacl()
