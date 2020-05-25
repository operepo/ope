
import os
import sys
import traceback
import logging

# try:
#     import _winreg as winreg
# except:
#     import winreg

import win32api    
#import winsys
from winsys import accounts, registry, security
from winsys.registry import REGISTRY_ACCESS

# Monkeypatch to force stuff in the registry class to do 64 bit registry access always even if we are a 32 bit process
registry.Registry.DEFAULT_ACCESS=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY

# Hide winsys logs
winsys_logger = logging.getLogger("winsys")
winsys_logger.setLevel(50)  # CRITIAL = 50

from color import p


class RegistrySettings:

    # All student accounts get added to this group
    STUDENTS_GROUP = "OPEStudents"
    ROOT_PATH = "HKLM\\Software\\OPE"


    @staticmethod
    def test_reg():
        print("Student: ", RegistrySettings.get_reg_value(value_name="laptop_student_name", default=""))
        print("Admin: ", RegistrySettings.get_reg_value(app="OPEService", value_name="laptop_admin_name", default="administrator"))

        RegistrySettings.set_reg_value(app="TESTOPE", value_name="TestValue", value="slkfjsdl")

        log_level = RegistrySettings.get_reg_value(app="OPEService", value_name="log_level", default=10,
            value_type="REG_DWORD")
        print("Log Level: ", log_level)


        # key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software\OPE", 0,
        #     winreg.KEY_WOW64_64KEY | winreg.KEY_READ)
        
        # p("SUB KEYS: ")
        # enum_done = False
        # i = 0
        # try:
        #     while enum_done is False:
        #         sub_key = winreg.EnumKey(key, i)
        #         p("-- SK: " + str(sub_key))
        #         i += 1
        #         # p("Ref: " + str(winreg.QueryReflectionKey(winreg.HKEY_LOCAL_MACHINE)))
        # except WindowsError as ex:
        #     # No more values
        #     if ex.errno == 22:
        #         # p("---_DONE")
        #         # Don't flag an error when we are out of entries
        #         pass
        #     else:
        #         p("-- ERR " + str(ex) + " " + str(ex.errno))
        #     pass
            
        #reg = registry.registry(r"HKLM\Software\OPETEST",
        #        access=REGISTRY_ACCESS.KEY_ALL_ACCESS|REGISTRY_ACCESS.KEY_WOW64_64KEY)
        #reg.create()

    @staticmethod
    def get_reg_value(root="", app="", subkey="", value_name="", default="",
        value_type=""):
        ret = default

        if root == "":
            root = RegistrySettings.ROOT_PATH

        # Combine parts
        path = os.path.join(root, app, subkey).replace("\\\\", "\\")
        # Make sure we don't have a tailing \\
        path = path.strip("\\")
        # print("path: " + path)

        try:
            # Open the key
            key = registry.registry(path, 
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            # Make sure the key exists
            key.create()
            
            val = key.get_value(value_name)
            # print("Got Val: " + str(val))

            if value_type == "REG_SZ":
                ret = str(val)
            elif value_type == "REG_DWORD":
                ret = int(val)
            else:
                ret = val
        except Exception as ex:
            #p("}}rbException! - Error pulling value from registry! Returning default value}}xx\n    (" +
            #    path + ":" + value_name + "=" + str(default_value)+")")
            #p(str(ex))
            pass

        return ret
    
    @staticmethod
    def set_reg_value(root="", app="", subkey="", value_name="", value="", value_type=""):
        ret = False

        if root == "":
            root = RegistrySettings.ROOT_PATH

        # Combine parts
        path = os.path.join(root, app, subkey).replace("\\\\", "\\")
        # Make sure we don't have a tailing \\
        path = path.strip("\\")
        # print("path: " + path)

        try:
            # Convert the value to the correct type
            if value_type == "REG_SZ":
                value = str(value)
            elif value_type == "REG_DWORD":
                value = int(value)
            
            # Open the key
            key = registry.registry(path, 
                access=REGISTRY_ACCESS.KEY_ALL_ACCESS|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            # Make sure the key exists
            key.create()
            key[value_name] = value
                        
            ret = True
        except Exception as ex:
            p("}}rbException! - Error setting registry value!}}xx\n    (" +
                path + ":" + value_name + "=" + str(value)+")")
            p(str(ex))
            pass

        return ret

    @staticmethod
    def set_default_ope_registry_permissions(student_user = "", laptop_admin_user = ""):
        try:
            if student_user == "":
                student_user = RegistrySettings.get_reg_value(value_name="laptop_student_name", default="")

            if laptop_admin_user == "":
                laptop_admin_user = RegistrySettings.get_reg_value(app="OPEService", value_name="laptop_admin_name", default="administrator")
            
            if laptop_admin_user == "":
                laptop_admin_user = None
            
            if student_user == "":
                p("}}rnNo credentialed student set!}}xx")
                #return False
                student_user = None
            
            # Make sure this user exists
            if student_user is not None:
                try:
                    # Will throw an exception if the user doesn't exist
                    student_p = accounts.principal(student_user)
                except Exception as ex:
                    # Invalid student account
                    p("}}rbInvalid Student Account - skipping permissions for this account: " + str(student_user) + "}}xx")
                    student_user = None
            
            # Make sure the admin user exists
            if laptop_admin_user is not None:
                try:
                    admin_p = accounts.principal(laptop_admin_user)
                except Exception as ex:
                    # Invalid admin account!
                    p("}}rbInvalid Admin Account - skipping permissions for this account: " + str(laptop_admin_user) + "}}xx")
                    laptop_admin_user = None

            base_dacl = [
                ("Administrators", registry.Registry.ACCESS["F"], "ALLOW"),
                ("System", registry.Registry.ACCESS["F"], "ALLOW"),
                #("Users", registry.Registry.ACCESS["Q"], "ALLOW")
            ]

            logged_in_user = win32api.GetUserName()
            if logged_in_user.upper() != "SYSTEM" and logged_in_user != "":
                base_dacl.append((logged_in_user, registry.Registry.ACCESS["F"], "ALLOW"),)

            if laptop_admin_user is not None and laptop_admin_user != "":
                # Make sure this admin has registry access
                base_dacl.append((laptop_admin_user, registry.Registry.ACCESS["F"], "ALLOW"))

            # Make sure the logging registry key has proper permissions
            reg = registry.registry(r"HKLM\System\CurrentControlSet\Services\EventLog\Application\OPE",
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                #s.dacl = base_dacl
                s.dacl.append(("Everyone",
                    REGISTRY_ACCESS.KEY_QUERY_VALUE | REGISTRY_ACCESS.KEY_SET_VALUE |
                    REGISTRY_ACCESS.KEY_ENUMERATE_SUB_KEYS | REGISTRY_ACCESS.KEY_NOTIFY,
                    "ALLOW"))
                # s.dacl.dump()

            reg = registry.registry(r"HKLM\Software\OPE",
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = base_dacl
                if student_user is not None:
                    s.dacl.append((student_user, registry.Registry.ACCESS["Q"], "ALLOW"))
                # s.dacl.dump()
            
            reg = registry.registry(r"HKLM\Software\OPE\OPELMS",
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = base_dacl
                if student_user is not None:
                    s.dacl.append((student_user, registry.Registry.ACCESS["Q"], "ALLOW"))
                # s.dacl.dump()
            
            reg = registry.registry(r"HKLM\Software\OPE\OPEService",
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = base_dacl
                #if student_user is not None:
                #    s.dacl.append((student_user, registry.Registry.ACCESS["Q"], "ALLOW"))
                # s.dacl.dump()
            
            reg = registry.registry(r"HKLM\Software\OPE\OPELMS\student",
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = base_dacl
                if student_user is not None:
                    s.dacl.append((student_user, registry.Registry.ACCESS["W"], "ALLOW"))
                # s.dacl.dump()

            p("}}gnRegistry Permissions Set}}xx")
        except Exception as ex:
            p("}}rbUnknown Exception! }}xx\n" + str(ex))
            traceback.print_exc()
            return False
        return True


if __name__ == "__main__":
    p("Running Tests...")
    RegistrySettings.test_reg()