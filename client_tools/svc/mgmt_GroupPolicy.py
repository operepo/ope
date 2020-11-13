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

        gpo_name = util.get_param(2, "exported_gpo")

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
        with os.scandir(gpo_folder) as it:
            for entry in it:
                if not entry.name.startswith(".") and entry.is_dir():
                    gpo_count += 1
        
        return gpo_count

    @staticmethod
    def apply_group_policy():
        ret = True

        if RegistrySettings.is_debug():
            p("}}rbDEBUG MODE ON - Skipping apply group policy}}xx")
            return True

        gpo_name = util.get_param(2, "gpo")

        # LGPO.exe is in the rc sub folder of the mgmt tool
        app_folder = util.get_app_folder()
        lgpo_path = os.path.join(app_folder, "rc")

        # Check to see if more then 1 folder exists in the gpo folder
        gpo_folder = os.path.join(lgpo_path, "gpo")
        gpo_count = GroupPolicy.get_gpo_count(gpo_folder)
        if gpo_count == 0:
            p("}}rbNO GPO FOLDER FOUND AT: " + gpo_folder + "\nPlease add your GPO settings to this folder to continue}}xx")
            return False
        if gpo_count > 1:
            p("}}rbTOO MANY GPO FOLDERS FOUND AT: " + gpo_folder + "\nRemove all but the newest GPO to continue!}}xx")
            return False
         
        cmd = "lgpo.exe /g " + gpo_name

        returncode, output = ProcessManagement.run_cmd(cmd, cwd=lgpo_path, attempts=5,
            require_return_code=0, cmd_timeout=30)
        if returncode == -2:
            # Unable to restore gpo?
            p("}}rnERROR - Unable to set group policy!}}xx\n" + output)
            ret = False
            return ret

        # Force gpupdate
        cmd = "%SystemRoot%\\system32\\gpupdate /force"
        returncode, output = ProcessManagement.run_cmd(cmd, attempts=5, 
            require_return_code=0, cmd_timeout=10)
        if returncode == -2:
            # Error running command?
            p("}}rnERROR - Unable to set force gpupdate!}}xx\n" + output)
            ret = False

        return ret

    @staticmethod
    def reset_group_policy_to_default():
        ret = True

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
            cmd_timeout=15)
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

        policy_file_name= util.get_param(2, "firewall_config.wfw")

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
        