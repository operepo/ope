import os
import sys
import shutil

from mgmt_ProcessManagement import ProcessManagement
from mgmt_RegistrySettings import RegistrySettings
import util
from color import p



class GroupPolicy:

    @staticmethod
    def export_group_policy():
        ret = True

        # Command that is run to start this function
        only_for = "export_group_policy"

        gpo_name = util.get_param(2, "exported_gpo", only_for=only_for)

        # LGPO.exe is in the rc sub folder of the mgmt tool
        app_folder = util.get_app_folder()
        lgpo_path = os.path.join(app_folder, "rc")
        gpo_path = os.path.join(lgpo_path, gpo_name)
        
        # NOTE - lgpo needs full path to gpo export directory
        cmd = "lgpo.exe /b \"" + gpo_path + "\""

        # Remove the folder if it exists
        p("Removing old files: " + gpo_path)
        shutil.rmtree(gpo_path, ignore_errors=True)

        # Folder has to exist
        os.makedirs(gpo_path, exist_ok=True)

        returncode, output = ProcessManagement.run_cmd(cmd, cwd=lgpo_path, attempts=5,
            require_return_code=0, cmd_timeout=15)
        if returncode == -2:
            # Unable to restore gpo?
            p("}}rnERROR - Unable to dump group policy!}}xx\n" + output)
            ret = False
            return ret
        p(output)

        return ret
    
    @staticmethod
    def get_gpo_count(gpo_folder=None):
        if gpo_folder is None:
            app_folder = util.get_app_folder()
            lgpo_path = os.path.join(app_folder, "rc")

            # Check to see if more then 1 folder exists in the gpo folder
            gpo_folder = os.path.join(lgpo_path, "gpo")

        gpo_count = 0
        try:
            with os.scandir(gpo_folder) as it:
                for entry in it:
                    if not entry.name.startswith(".") and entry.is_dir():
                        gpo_count += 1
        except:
            pass
        return gpo_count

    @staticmethod
    def apply_group_policy():
        ret = True

        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping apply group policy}}xx")
            return True

        # Command that is run to start this function
        only_for = "apply_group_policy"

        gpo_name = util.get_param(2, "gpo", only_for=only_for)
        gpo_name_pre = gpo_name + "_pre"
        gpo_name_post = gpo_name + "_post"

        # LGPO.exe is in the rc sub folder of the mgmt tool
        app_folder = util.get_app_folder()
        lgpo_path = os.path.join(app_folder, "rc")

        # Check to see if more then 1 folder exists in the gpo folder
        gpo_folder = os.path.join(lgpo_path, gpo_name)
        gpo_folder_pre = os.path.join(lgpo_path, gpo_name_pre)
        gpo_folder_post = os.path.join(lgpo_path, gpo_name_post)
        gpo_count = GroupPolicy.get_gpo_count(gpo_folder)
        gpo_count_pre = GroupPolicy.get_gpo_count(gpo_folder_pre)
        gpo_count_post = GroupPolicy.get_gpo_count(gpo_folder_post)
        if gpo_count == 0:
            p("}}rbNO GPO FOLDER FOUND AT: " + gpo_folder + "\nPlease add your GPO settings to this folder to continue}}xx")
            return False
        if gpo_count > 1:
            p("}}rbTOO MANY GPO FOLDERS FOUND AT: " + gpo_folder + "\nRemove all but the newest GPO to continue!}}xx")
            return False
        if gpo_count_pre > 1:
            p("}}rbTOO MANY GPO FOLDERS FOUND AT: " + gpo_folder_pre + "\nRemove all but the newest GPO to continue!}}xx")
            return False
        if gpo_count_post > 1:
            p("}}rbTOO MANY GPO FOLDERS FOUND AT: " + gpo_folder_post + "\nRemove all but the newest GPO to continue!}}xx")
            return False

        # Make sure to reset to default before applying
        GroupPolicy.reset_group_policy_to_default()

        # Apply gpo_pre if it exists
        errors = False
        if gpo_count_pre == 1:
            cmd = "lgpo.exe /g " + gpo_name_pre
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=lgpo_path, attempts=5,
                require_return_code=0, cmd_timeout=60)
            if returncode == -2:
                # Unable to restore gpo?
                p("}}rnERROR - Unable to set group policy - %s!}}xx\n %s" % (gpo_folder_pre, output) )
                errors = True
        
        if gpo_count == 1:
            cmd = "lgpo.exe /g " + gpo_name

            returncode, output = ProcessManagement.run_cmd(cmd, cwd=lgpo_path, attempts=5,
                require_return_code=0, cmd_timeout=60)
            if returncode == -2:
                # Unable to restore gpo?
                p("}}rnERROR - Unable to set group policy - %s!}}xx\n %s" % (gpo_folder, output) )
                errors = True
        
        if gpo_count_post == 1:
            cmd = "lgpo.exe /g " + gpo_name_post
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=lgpo_path, attempts=5,
                require_return_code=0, cmd_timeout=60)
            if returncode == -2:
                # Unable to restore gpo?
                p("}}rnERROR - Unable to set group policy - %s!}}xx\n %s" % (gpo_folder_post, output) )
                errors = True

        # Force gpupdate
        cmd = "%SystemRoot%\\system32\\gpupdate /force"
        returncode, output = ProcessManagement.run_cmd(cmd, attempts=5,
            require_return_code=0, cmd_timeout=60, shell=False)
        if returncode == -2:
            # Error running command?
            p("}}rnERROR - Unable to set force gpupdate!}}xx\n" + output)
            ret = False

        if errors is True:
            ret = False
        
        return ret

    @staticmethod
    def reset_group_policy_to_default(force=False):
        ret = True

        # Use WMI to check if gpo is applied, if not, skip
        if force != True:
            try:
                from mgmt_Computer import Computer
                w = Computer.get_wmi_connection(namespace="root\\rsop\\computer")
                registry_policies = w.RSOP_RegistryPolicySetting()
                policies = w.RSOP_PolicySetting()
                if len(registry_policies) == 0 and len(policies) == 0:
                    p("}}gn - No Group Policy Objects Dected, skipping gpo reset...}}xx")
                    return True
            except Exception as ex:
                p("}}rb - Failed to check group policy objects! Falling to hard reset.}}xx")
                p(f"{ex}")
                return False

        # Need to reset secpol.msc settings
        cmd = "%SystemRoot%\\system32\\secedit /configure /cfg %SystemRoot%\\inf\\defltbase.inf /db %SystemRoot%\\system32\\defltbase.sdb /verbose " # 2>NUL 1<NUL"

        returncode, output = ProcessManagement.run_cmd(cmd)
        # NOTE - This command always runs w warnings - returncode 3
        #p(output)
        if returncode == -2:
            # Error running command?
            ret = False
                
        # Remove the group policy objects
        cmd = "rd /S /Q \"%SystemRoot%\\System32\\GroupPolicyUsers\" & " + \
            "rd /S /Q \"%SystemRoot%\\System32\\GroupPolicy\" "
        returncode, output = ProcessManagement.run_cmd(cmd)
        if returncode == -2:
            # Error running command?
            ret = False
        
        #p(str(returncode))
        #p(output)

        cmd = "%SystemRoot%\\system32\\gpupdate /force"
        returncode, output = ProcessManagement.run_cmd(cmd, attempts=5, require_return_code=0,
            cmd_timeout=60, shell=False)
        if returncode == -2:
            # Error running command?
            ret = False
        
        #p("Ret: " + str(returncode) + " \n" + output)

        if ret is True:
            p("}}gnDone - Group policy reset to default.}}xx")
        else:
            p("}}rn*** WARNING *** There were issues resetting the windows group policy settings!}}xx")

        return ret
    
    @staticmethod
    def apply_firewall_policy():
        ret = True
        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping apply firewall policy}}xx")
            return True

        # Command that is run to start this function
        only_for = "apply_firewall_policy"

        policy_file_name= util.get_param(2, "firewall_config.wfw", only_for=only_for)

        # Should be in RC sub folder under the app
        app_folder = util.get_app_folder()
        rc_path = os.path.join(app_folder, "rc")
        policy_file_path = os.path.join(rc_path, policy_file_name)

        # netsh advfirewall import "%~dp0rc\firewall_config.wfw" 2>NUL 1<NUL
        
        cmd = "%SystemRoot%\\system32\\netsh advfirewall import \"" + policy_file_path + "\""
        returncode, output = ProcessManagement.run_cmd(cmd, attempts=5, require_return_code=0,
            cmd_timeout=15)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to reset firewall back to defaults?}}xx\n" + output)
            ret = False
        
        return ret

    @staticmethod
    def reset_firewall_policy():
        ret = True
        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping reset firewall policy}}xx")
            return True

        cmd = "%SystemRoot%\\system32\\netsh advfirewall reset"
        returncode, output = ProcessManagement.run_cmd(cmd, attempts=5, require_return_code=0,
            cmd_timeout=15)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to reset firewall back to defaults?}}xx\n" + output)
            ret = False

        # rem reset settings to default
        # netsh advfirewall reset
        # rem turn on all profiles
        # rem netsh advfirewall set allprofiles state on
        # rem turn on logging
        # rem netsh advfirewall set currentprofile logging filename "c:\programdata\ope\tmp\log\pfirewall.log"

        return ret

    def run_tests():
        # Check long running processes
        cmd = "%SystemRoot%\\system32\\gpupdate /force"
        #cmd = "timeout 60"
        returncode, output = ProcessManagement.run_cmd(cmd, attempts=5, require_return_code=0,
            cmd_timeout=35, shell=False)
        if returncode == -2:
            # Error running command?
            ret = False
            p("}}rbError: Unable to run cmd: %s}}xx" % cmd)
        return

if __name__ == "__main__":
    GroupPolicy.run_tests()        