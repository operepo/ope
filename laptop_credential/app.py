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

import win_util

ssl._create_default_https_context = ssl._create_unverified_context

admin_user = "admin"
admin_pass = ""
smc_url = "https://smc.ed.dev"
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

    term.p(txt)


def print_checklist_warning():
    # Print a warning reminding IT staff to properly secure the laptop in the Bios

    txt = """
}}mn======================================================================
}}mn| }}ybWARNING: }}dnEnsure that the boot from USB or boot from SD card        }}mn|
}}mn| }}dnoptions in the bios are disabled and that the admin password is    }}mn|
}}mn| }}dnset to a strong random password.                                   }}mn|
}}mn======================================================================}}dn
    """

    term.p(txt)




def main():
    global admin_user, admin_pass, smc_url, student_user, server_name, home_root
    canvas_access_token = ""


    print_app_header()
    # Ask for admnin user/pass and website
    tmp = raw_input( term.translateColorCodes("}}ynPlease enter the ADMIN user name }}cn[enter for default " + admin_user + "]:}}dn "))
    tmp = tmp.strip()
    if tmp == "":
        tmp = admin_user
    admin_user = tmp

    tmp = getpass.getpass("Please enter ADMIN password: ")
    if tmp == "":
        print("A password is required.")
        sys.exit()
    admin_pass = tmp

    tmp = raw_input("Enter URL for SMC Server [enter for default " + smc_url + "]: ")
    tmp = tmp.strip()
    if tmp == "":
        tmp = smc_url
    smc_url = tmp

    tmp = ""
    while tmp.strip() == "":
        tmp = raw_input("Please enter the username for the student: ")
    student_user = tmp.strip()

    print("Setup computer with: ")
    print("\tAdmin User: " + admin_user)
    print("\tAdmin Pass: *******")
    print("\tSMC URL: " + smc_url)
    print("\tStudent Username: " + student_user)
    tmp = raw_input("Press Y to continue: ")
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

        print("Getting Canvas Auth Key...")
        url = api_url + "lms/credential_student.json/" + student_user

        request = urllib2.Request(url, None, headers)
        response = urllib2.urlopen(request)

        json_str = response.read()
        canvas_response = json.loads(json_str)
        canvas_access_token = str(canvas_response["key"])
        hash = str(canvas_response["hash"])
        student_full_name = str(canvas_response["full_name"])

        #print("Response: " + canvas_access_token + " ---- " + hash)
        pw = win_util.decrypt(hash, canvas_access_token)

        print("Creating Windows User...")
        win_util.create_local_student_account(student_user, student_full_name, pw)


        # Store the access token in the registry where the LMS app can pick it up
        key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS", student_user)
        key = win_util.create_reg_key(r"HKLM\Software\OPE\OPELMS\student")
        key.canvas_access_token = canvas_access_token

        print("Installing Admin Services...")

        print("Installing offline LMS app...")

        print ("Applying security rules...")

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

        a = raw_input("Press enter when done")




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
