
import os
import sys
import traceback
import logging
import time
import json

# try:
#     import _winreg as winreg
# except:
#     import winreg

import win32api    
# Make sure to import root winsys for exceptions
import winsys
from winsys import accounts, registry, security
from winsys.registry import REGISTRY_ACCESS

# Monkeypatch to force stuff in the registry class to do 64 bit registry access always even if we are a 32 bit process
registry.Registry.DEFAULT_ACCESS=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY

# Hide winsys logs
winsys_logger = logging.getLogger("winsys")
winsys_logger.setLevel(50)  # CRITIAL = 50

from color import p
import util

class RegistrySettings:
    # Default registry path where settings are stored    
    ROOT_PATH = "HKLM\\Software\\OPE"


    @staticmethod
    def get_credentialed_student_username():
        # Get credentialed student username
        student_user = RegistrySettings.get_reg_value(app="OPELMS\\student", value_name="user_name", default="")
        laptop_network_type = RegistrySettings.get_reg_value(app="OPEService", value_name="laptop_network_type", default="Stand Alone")
        laptop_domain_name = RegistrySettings.get_reg_value(app="OPEService", value_name="laptop_domain_name", default="osn.local")

        ret = student_user
        if student_user != "" and laptop_network_type == "Domain Member" and laptop_domain_name != "":
            ret = laptop_domain_name + "\\" + student_user
        
        return ret

    @staticmethod
    def is_debug():
        val = RegistrySettings.get_reg_value(value_name="debug", default="off")
        if val == "on":
            return True
        
        return False
    
    @staticmethod
    def is_machine_locked():
        val = RegistrySettings.get_reg_value(app="OPEService", value_name="machine_locked", default="no")
        if val == "yes":
            return True
        
        return False

    @staticmethod
    def set_machine_locked(locked=False):
        val = "no"
        if locked is True:
            val = "yes"
        RegistrySettings.set_reg_value(app="OPEService", value_name="machine_locked", value=val)
        return True

    @staticmethod
    def reset_timer(timer_name="default_timer"):
        RegistrySettings.set_reg_value(value_name=timer_name, value=time.time())
        return True

    @staticmethod
    def is_timer_expired(timer_name="default_timer", time_span=60, auto_reset_timer=True):
        # How long has it been since we talked to the SMC server?
        last_smc_ping_time = RegistrySettings.get_reg_value(value_name=timer_name, default=0)
        curr_time = time.time()

        # Only need a successful ping every ? minutes
        min_time = time_span
        time_diff = curr_time - last_smc_ping_time
        if time_diff > min_time:
            # Timer ran out

            if auto_reset_timer is True:
                p("Auto Reset Timer: " + timer_name, log_level=5)
                RegistrySettings.reset_timer(timer_name=timer_name)
            return True
        
        #p("}}ynNot time to ping yet - " + str(int(min_time - time_diff)) + " seconds left.}}xx", log_level=4)
        return False

    @staticmethod
    def test_reg():
        # canvas_access_token = "2043582439852400"
        # canvas_url = "https://canvas.ed"
        # smc_url = "https://smc.ed"
        # student_user = "777777"
        # student_name = "Bob Smith"
        # admin_user = "huskers"
        
        RegistrySettings.set_reg_value(app="OPELMS\\student", value_name="smc_url_test",
            value="https://smc.ed", value_type="REG_SZ")

        #RegistrySettings.store_credential_info(canvas_access_token, canvas_url, smc_url,
        #    student_user, student_name, admin_user)
        p("Student: " + RegistrySettings.get_reg_value(value_name="student_user", default=""))
        p("Admin: " + RegistrySettings.get_reg_value(app="OPEService", value_name="admin_user", default="administrator"))

        #RegistrySettings.set_reg_value(app="TESTOPE", value_name="TestValue", value="slkfjsdl")

        log_level = RegistrySettings.get_reg_value(app="OPEService", value_name="log_level", default=10,
            value_type="REG_DWORD")
        p("Log Level: ", log_level)


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
    def add_mgmt_utility_to_path():
        # Add the mgmt utility path environment variable

        # System env path
        # HLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
        # User path
        # HKEY_CURRENT_USER\Environment\Path
        # Application Path
        # HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\

        # Grab the system path variable

        sys_path = RegistrySettings.get_reg_value(root="HKLM\\SYSTEM\\CurrentControlSet",
            app="Control", subkey="Session Manager\\Environment",
            value_name="Path", default="")
        
        if sys_path == "":
            p("}}rbUnable to grab System path variable!}}xx")
            return False
        
        mgmt_path = "%programdata%\\ope\\Services\\mgmt\\"
        if not mgmt_path in sys_path:
            sys_path += ";" + mgmt_path
        
            #p("}}ynNew Path: " + sys_path + "}}xx")

            RegistrySettings.set_reg_value(root="HKLM\\SYSTEM\\CurrentControlSet",
                app="Control", subkey="Session Manager\\Environment",
                value_name="Path", value=sys_path)
        
            p("}}gnmgmt.exe Added to system path.")
            p("}}gbYou will need to open a new command prompt for the change to take effect.}}xx")
        else:
            p("}}gnmgmt.exe Already in the system path.")
    
        return True

    @staticmethod
    def remove_key(key_path):
        try:
            # Open the key
            key = registry.registry(key_path, 
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            key.delete()
        except Exception as ex:
            p("}}rnError - couldn't remove registry key }}xx\n" + str(key_path) + "\n" + \
                str(ex), debug_level=1)
            return False
        
        return True

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
        #p("path: " + path)

        try:
            # Open the key
            key = registry.registry(path, 
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            # Make sure the key exists
            key.create()
            
            val = key.get_value(value_name)
            
            # p("Got Val: " + str(val))

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
            if ex is None:
                # Make pylint shut up
                pass
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
        # p("path: " + path)

        reg_type = None

        try:
            # Convert the value to the correct type
            if value_type == "REG_SZ":
                #p("}}ynSetting To String}}xx")
                value = str(value)
                reg_type = registry.REGISTRY_VALUE_TYPE.REG_SZ
            elif value_type == "REG_DWORD":
                value = int(value)
                reg_type = registry.REGISTRY_VALUE_TYPE.REG_DWORD
            elif value_type == "REG_BINARY":
                value = value
                reg_type = registry.REGISTRY_VALUE_TYPE.REG_BINARY
            elif value_type == "REG_QWORD":
                value = value
                reg_type = registry.REGISTRY_VALUE_TYPE.REG_QWORD
            elif value_type == "":
                # Try to guess
                if type(value) is float:
                    reg_type = registry.REGISTRY_VALUE_TYPE.REG_QWORD
                    value = int(value)
                
            
            # Open the key
            key = registry.registry(path, 
                access=REGISTRY_ACCESS.KEY_ALL_ACCESS|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            # Make sure the key exists
            key.create()
            key.set_value(value_name, value, reg_type)
            #key[value_name] = value
                        
            ret = True
        except Exception as ex:
            p("}}rbException! - Error setting registry value!}}xx\n\t(" +
                path + ":" + value_name + "=" + str(value)+")")
            p("\t" + str(ex))
            traceback.print_stack()
            pass

        return ret

    @staticmethod
    def get_git_branch():
        # If branch is still empty, get it from the registry
        curr_branch = RegistrySettings.get_reg_value(value_name="install_branch", default="master")
        p("}}gnUsing Branch: " + curr_branch + "}}xx")
        return curr_branch

    @staticmethod
    def set_git_branch(branch=None):
        # Command that is run to start this function
        only_for = "set_git_branch"

        curr_branch = branch
        if curr_branch is None:
            # See if a parameter was provided
            curr_branch = util.get_param(2, None, only_for=only_for)

        if curr_branch is None:
            curr_branch = "master"
        ret = RegistrySettings.set_reg_value(value_name="install_branch", value=curr_branch, value_type="REG_SZ")
        if ret is False:
            p("}}ybUnable to set git branch to " + curr_branch + "}}xx")
            return False
        else:
            p("}}gnGit branch set to: " + curr_branch + "}}xx")
            return True

    @staticmethod
    def store_smc_config(config_dict):
        # Example config_dict
        # {"smc_version": "v1.9.41", "laptop_network_type": "Domain Member", "laptop_domain_name": "osn.local", "laptop_domain_ou": "laptops.osn.local", "laptop_time_servers": ["time.windows.com", "smc.ed", "osn.local"], "laptop_approved_nics": ["Realtek RTL8139C+ Fast Ethernet NIC==192.168.0.", "ZeroTier Virtual Port==192.168.222."]}

        smc_version = config_dict.get("smc_version", "MISSING")
        RegistrySettings.set_reg_value(app="", value_name="smc_version", value=smc_version, value_type="REG_SZ")

        laptop_network_type = config_dict.get("laptop_network_type", "Stand Alone")
        RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_network_type", value=laptop_network_type, value_type="REG_SZ")

        laptop_domain_name = config_dict.get("laptop_domain_name", "osn.local")
        RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_domain_name", value=laptop_domain_name, value_type="REG_SZ")

        laptop_domain_ou = config_dict.get("laptop_domain_ou", "laptops.osn.local")
        RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_domain_ou", value=laptop_domain_ou, value_type="REG_SZ")

        try:
            laptop_time_servers = config_dict.get("laptop_time_servers", [])
            laptop_time_servers_json = json.dumps(laptop_time_servers)
            RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_time_servers", value=laptop_time_servers_json)
        except Exception as ex:
            p("}}rbError storing time servers: " + str(ex) + "}}xx")

        try:
            laptop_approved_nics = config_dict.get("laptop_approved_nics", [])
            # Convert nic==ip format to a array of tuples
            current_nics_json = RegistrySettings.get_reg_value(app="OPEService", value_name="laptop_approved_nics", default="[]")
            current_nics = json.loads(current_nics_json)
            
            for nic in laptop_approved_nics:
                parts = nic.split("==")
                #p("}}ynParts: " + str(parts) + "}}xx")
                if len(parts) == 2:
                    n = (parts[0], parts[1])
                    if n not in current_nics:
                        current_nics.append(n)
                else:
                    p("}}rnInvalid NIC format: " + str(nic) + "}}xx")
                
            
            current_nics_json = json.dumps(current_nics)
            #p("}}gnApproved NICs: " + str(current_nics_json) + "}}xx")
            RegistrySettings.set_reg_value(app="OPEService", value_name="approved_nics", value=current_nics_json)
        except Exception as ex:
            p("}}rbError storing approved nics: " + str(ex) + "}}xx")
            
        return True

    @staticmethod
    def store_credential_info(canvas_access_token, canvas_url, smc_url,
            student_user, student_name, admin_user,
            laptop_network_type, laptop_domain_name, laptop_domain_ou):
        # Store credential info in the proper places
        RegistrySettings.set_reg_value(app="", value_name="canvas_access_token",
            value=canvas_access_token, value_type="REG_SZ")
        RegistrySettings.set_reg_value(app="OPELMS\\student", value_name="canvas_access_token",
            value=canvas_access_token, value_type="REG_SZ")

        RegistrySettings.set_reg_value(app="", value_name="canvas_url", value=canvas_url,
            value_type="REG_SZ")
        RegistrySettings.set_reg_value(app="OPELMS\\student", value_name="canvas_url",
            value=canvas_url, value_type="REG_SZ")

        RegistrySettings.set_reg_value(app="", value_name="smc_url", value=smc_url,
            value_type="REG_SZ")
        RegistrySettings.set_reg_value(app="OPELMS\\student", value_name="smc_url",
            value=smc_url, value_type="REG_SZ")

        RegistrySettings.set_reg_value(app="", value_name="student_user", value=student_user,
            value_type="REG_SZ")
        RegistrySettings.set_reg_value(app="OPELMS\\student", value_name="user_name",
            value=student_user, value_type="REG_SZ")

        RegistrySettings.set_reg_value(app="", value_name="student_name", value=student_name,
            value_type="REG_SZ")

        RegistrySettings.set_reg_value(app="OPEService", value_name="admin_user", value=admin_user,
            value_type="REG_SZ")
        
        RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_network_type", value=laptop_network_type,
            value_type="REG_SZ")
        
        RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_domain_name", value=laptop_domain_name,
            value_type="REG_SZ")
        
        RegistrySettings.set_reg_value(app="OPEService", value_name="laptop_domain_ou", value=laptop_domain_ou,
            value_type="REG_SZ")

        return True

    @staticmethod
    def is_time_to_set_default_ope_registry_permissions():
        # How long has it been since we synced our time?
        last_time_sync = RegistrySettings.get_reg_value(value_name="last_apply_ope_registry_permissions", default=0)
        curr_time = time.time()

        set_default_permissions_timer = RegistrySettings.get_reg_value(value_name="apply_ope_registry_permissions_timer", default=3600*3)

        # Only sync every ?? minutes
        if curr_time - last_time_sync > set_default_permissions_timer:
            return True
        
        return False

    @staticmethod
    def set_default_ope_registry_permissions(student_user = "", laptop_admin_user = "", force=False):
        only_for="set_default_ope_registry_permissions"
        param_force = util.pop_force_flag(only_for=only_for)
        if force is False:
            force = param_force
        
        if not force is True and not RegistrySettings.is_time_to_set_default_ope_registry_permissions():
            p("}}gnNot time to set ope registry permissions yet, skipping.}}xx", log_level=4)
            return True
        
        RegistrySettings.set_reg_value(value_name="last_apply_ope_registry_permissions", value=time.time(), value_type="REG_DWORD")

        try:
            p("}}gnTrying to set OPE Registry Permissions...}}xx", log_level=3)
            if student_user == "":
                student_user = RegistrySettings.get_reg_value(value_name="student_user", default="")

            if laptop_admin_user == "":
                laptop_admin_user = RegistrySettings.get_reg_value(app="OPEService", value_name="admin_user", default="administrator")
            
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
                    if student_p is None:
                        # Get pylint to shutup
                        pass
                except Exception as ex:
                    # Invalid student account
                    p("}}rbInvalid Student Account - skipping permissions for this account: " + str(student_user) + "}}xx")
                    student_user = None
            # NOTE - Stop addding student user - add opestudent group instead
            student_user = None
            
            # Discontinue admin account creation
            # # Make sure the admin user exists
            # from mgmt_Computer import Computer
            # if not Computer.is_domain_joined() and laptop_admin_user is not None:
            #     try:
            #         admin_p = accounts.principal(laptop_admin_user)
            #         if admin_p is None:
            #             # Get pylint to shutup
            #             pass
            #     except Exception as ex:
            #         # Invalid admin account!
            #         p("}}rbInvalid Admin Account - skipping permissions for this account: " + str(laptop_admin_user) + "}}xx")
            #         laptop_admin_user = None

            base_dacl = [
                ("Administrators", registry.Registry.ACCESS["F"], "ALLOW"),
                ("SYSTEM", registry.Registry.ACCESS["F"], "ALLOW"),
                ("OPEAdmins", registry.Registry.ACCESS["F"], "ALLOW"),
                #("Users", registry.Registry.ACCESS["Q"], "ALLOW")
            ]
            service_base_dacl = [
                ("Administrators", registry.Registry.ACCESS["F"], "ALLOW"),
                ("SYSTEM", registry.Registry.ACCESS["F"], "ALLOW"),
                ("OPEAdmins", registry.Registry.ACCESS["F"], "ALLOW"),
                # Don't let regular users read OPEService key
                #("Users", registry.Registry.ACCESS["Q"], "ALLOW")
            ]

            #logged_in_user = win32api.GetUserName()
            logged_in_user = win32api.GetUserNameEx(win32api.NameSamCompatible)
            if not "SYSTEM" in logged_in_user.upper() and logged_in_user != "":
                base_dacl.append((logged_in_user, registry.Registry.ACCESS["F"], "ALLOW"))
                service_base_dacl.append((logged_in_user, registry.Registry.ACCESS["F"], "ALLOW"))

            # Discontinue admin account creation
            # if not Computer.is_domain_joined() and laptop_admin_user is not None and laptop_admin_user != "":
            #     # Make sure this admin has registry access
            #     base_dacl.append((laptop_admin_user, registry.Registry.ACCESS["F"], "ALLOW"))
            #     service_base_dacl.append((laptop_admin_user, registry.Registry.ACCESS["F"], "ALLOW"))

            try:
                # Make sure the logging registry key has proper permissions
                reg = registry.registry(r"HKLM\System\CurrentControlSet\Services\EventLog\Application\OPE",
                    access=REGISTRY_ACCESS.KEY_ALL_ACCESS|REGISTRY_ACCESS.KEY_WOW64_64KEY)
                reg.create()
                with reg.security() as s:
                    # Break inheritance causes things to reapply properly
                    s.break_inheritance(copy_first=True)
                    s.owner = accounts.principal("Administrators")
                    #s.dacl = base_dacl
                    s.dacl.append(("Everyone",
                        registry.Registry.ACCESS["R"],
                        "ALLOW"))
                    # s.dacl.dump()
            except Exception as ex:
                p("}}ybUnkown Error trying to register OPE Event source:}}xx " + str(ex))
                p(traceback.format_exc())
                p("This isn't critical. To try again, try running:\n mgmt set_default_ope_registry_permissions -f ")


            reg = registry.registry(r"HKLM\Software\OPE",
                access=REGISTRY_ACCESS.KEY_ALL_ACCESS|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = base_dacl
                if student_user is not None:
                    s.dacl.append((student_user, registry.Registry.ACCESS["R"], "ALLOW"))
                s.dacl.append(("Everyone",
                    registry.Registry.ACCESS["R"],
                    "ALLOW"
                ))
                s.dacl.append(("OPEStudents",
                    registry.Registry.ACCESS["R"],
                    "ALLOW"
                ))
                # s.dacl.dump()
            
            reg = registry.registry(r"HKLM\Software\OPE\OPELMS",
                access=REGISTRY_ACCESS.KEY_ALL_ACCESS|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = base_dacl
                if student_user is not None:
                    s.dacl.append((student_user, registry.Registry.ACCESS["C"],
                    "ALLOW"))
                s.dacl.append(("Everyone",
                    registry.Registry.ACCESS["R"],
                    "ALLOW"
                ))
                s.dacl.append(("OPEStudents",
                    registry.Registry.ACCESS["R"],
                    "ALLOW"
                ))
                # s.dacl.dump()
            
            reg = registry.registry(r"HKLM\Software\OPE\OPEService",
                access=REGISTRY_ACCESS.KEY_READ|REGISTRY_ACCESS.KEY_WOW64_64KEY)
            reg.create()
            with reg.security() as s:
                # Break inheritance causes things to reapply properly
                s.break_inheritance(copy_first=True)
                s.dacl = service_base_dacl
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
                    s.dacl.append((student_user, registry.Registry.ACCESS["C"],
                    "ALLOW"))
                s.dacl.append(("Everyone",
                    registry.Registry.ACCESS["R"],
                    "ALLOW"
                ))
                s.dacl.append(("OPEStudents",
                    registry.Registry.ACCESS["R"],
                    "ALLOW"
                ))
                # s.dacl.dump()

            p("}}gnRegistry Permissions Set}}xx", log_level=3)
        except Exception as ex:
            p("}}rbUnknown Exception! }}xx\n" + str(ex))
            p(traceback.format_exc())
            return False
        return True

    @staticmethod
    def set_screen_shot_timer():
        # Command that is run to start this function
        only_for = "set_screen_shot_timer"

        # Set how often to reload scan nics
        param = util.get_param(2, "", only_for=only_for)
        if param == "":
            p("}}rnInvalid frequency Specified}}xx")
            return False
        
        frequency = "30-300"
        try:
            frequency = str(param)
        except:
            # Not an int? Set it as a string
            frequency = param
            #p("}}rnInvalid frequency Specified}}xx")
            #return False

        # Set the registry setting
        RegistrySettings.set_reg_value(app="OPEService", value_name="screen_shot_timer",
            value=frequency)
        return True

    @staticmethod
    def set_log_level():
        # Command that is run to start this function
        only_for = "set_log_level"

        # Set the log level parameter in the registry
        param = util.get_param(2, "", only_for=only_for)
        if param == "":
            p("}}rnInvalid Log Level Specified}}xx")
            return False
        
        log_level = 3
        try:
            log_level = int(param)
        except:
            p("}}rnInvalid Log Level Specified}}xx")
            return False

        # Set the registry setting
        RegistrySettings.set_reg_value(app="OPEService", value_name="log_level", value=log_level)
        return True

    @staticmethod
    def set_default_permissions_timer():
        # Command that is run to start this function
        only_for = "set_default_permissions_timer"

        # Set how often to reset permissions in the registry
        param = util.get_param(2, "", only_for=only_for)
        if param == "":
            p("}}rnInvalid frequency Specified}}xx")
            return False
        
        frequency = 3600
        try:
            frequency = int(param)
        except:
            p("}}rnInvalid frequency Specified}}xx")
            return False

        # Set the registry setting
        RegistrySettings.set_reg_value(app="OPEService", value_name="set_default_permissions_timer", value=frequency)
        return True

    @staticmethod
    def set_reload_settings_timer():
        # Command that is run to start this function
        only_for = "set_reload_settings_timer"

        # Set how often to reload settings from the registry
        param = util.get_param(2, "", only_for=only_for)
        if param == "":
            p("}}rnInvalid frequency Specified}}xx")
            return False
        
        frequency = 30
        try:
            frequency = int(param)
        except:
            p("}}rnInvalid frequency Specified}}xx")
            return False

        # Set the registry setting
        RegistrySettings.set_reg_value(app="OPEService", value_name="reload_settings_timer", value=frequency)
        return True

    @staticmethod
    def set_scan_nics_timer():
        # Command that is run to start this function
        only_for = "set_scan_nics_timer"

        # Set how often to reload scan nics
        param = util.get_param(2, "", only_for=only_for)
        if param == "":
            p("}}rnInvalid frequency Specified}}xx")
            return False
        
        frequency = 60
        try:
            frequency = int(param)
        except:
            p("}}rnInvalid frequency Specified}}xx")
            return False

        # Set the registry setting
        RegistrySettings.set_reg_value(app="OPEService", value_name="scan_nics_timer", value=frequency)
        return True


if __name__ == "__main__":
    p("Running Tests...")
    #RegistrySettings.test_reg()

    while True:
        r = RegistrySettings.is_timer_expired(timer_name="test_timer", time_span=10)
        print("Timer: " + str(r))
        time.sleep(1)
    
