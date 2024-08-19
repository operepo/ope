import os
import sys
import subprocess
import ctypes
import shutil
import datetime

import win32security
import win32process
import win32con
import win32profile

import util
from color import p

from mgmt_UserAccounts import UserAccounts
from mgmt_RegistrySettings import RegistrySettings

# NOTE - Need to disable 32bit/64bit file redirection when running on a 64 bit system!
class disable_file_system_redirection:
    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
    def __enter__(self):
        self.old_value = ctypes.c_long()
        self.success = self._disable(ctypes.byref(self.old_value))
    def __exit__(self, type, value, traceback):
        if self.success:
            self._revert(self.old_value)



class ProcessManagement:

    @staticmethod
    def run_process_as_user(cmd, cwd=None, user_name=None):
        # Execute process as the user in question.
        ret = False
        p("run_process_as_user -- NOT DONE YET!")
        return False

        # Get the user name
        if user_name is None:
            # Get the current user name
            user_name = UserAccounts.get_active_user_name()
        
        # Get the user token for this user
        user_token = UserAccounts.get_user_token(user_name)
        if user_token is None:
            p("Unable to get user token!", log_level=1)
            return False
        
        user_token.impersonate()
        
        p("}}gnRunning Process as user: " + str(cmd) + "}}xx", log_level=5)

        # Use win create process function
        si = win32process.STARTUPINFO()
        si.dwFlags = win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_NORMAL
        # si.lpDesktop = "WinSta0\Default"   ## For secure desktop, "WinSta0\\Winlogon"
        si.lpDesktop = "WinSta0\\Default"

        # Setup envinroment for the user
        environment = win32profile.CreateEnvironmentBlock(user_token, False)

        try:
            (hProcess, hThread, dwProcessId, dwThreadId) = win32process.CreateProcess(
                                            #user_token,    # Using impersonation for this
                                            None,   # AppName (really command line, blank if cmd line supplied)
                                            "\"" + cmd + "\"",  # Command Line (blank if app supplied)
                                            None,  # Process Attributes
                                            None,  # Thread Attributes
                                            0,  # Inherits Handles
                                            win32con.CREATE_NEW_CONSOLE | win32con.NORMAL_PRIORITY_CLASS,  # or win32con.CREATE_NEW_CONSOLE,
                                            environment,  # Environment
                                            os.path.dirname(cmd),  # Curr directory
                                            si)  # Startup info
            hThread = hThread  # Make pylint chill
            dwThreadId = dwThreadId # make pylint chill
            p("Process Started: " + str(dwProcessId), log_level=5)
            p(hProcess, log_level=5)
            ret = True
        except Exception as e:
            p("}}rnError launching process:}}xx\n" + str(e), log_level=1)
            
        # Cleanup
        user_token.close()

        if ret is True:
            p("}}gnProcess executed. }}xx" + str(cmd), log_level=5)
        return ret

    @staticmethod
    def run_detatched_cmd(cmd, attempts=1, cmd_timeout=20, require_return_code=None, cwd=None):
        # Constants needed until python 3.7
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008
        
        try:
            cmd = os.path.expandvars(cmd)
            proc = subprocess.Popen(cmd, bufsize=0, close_fds=True,
                #stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
            proc = proc # make pylint chill
        except Exception as ex:
            p("}}rbError running detatched command! " + cmd + "}}xx\n" + str(ex))
            return False

        return True

    @staticmethod
    def run_cmd(cmd, attempts=1, cmd_timeout=120, require_return_code=None, cwd=None, shell=True):
        ret = (-2, "")
        # NOTE - if shell=True then timeout doesn't work properly!
        # Make sure we replace %programdata% style values
        cmd = os.path.expandvars(cmd)

        cmd_succeded = False
        while not cmd_succeded:
            try:
                p("Running cmd (attempt " + str(attempts) + "): " + cmd)
                with disable_file_system_redirection():
                    proc = subprocess.run(cmd, shell=shell, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, timeout=cmd_timeout, cwd=cwd)
                    
                out = proc.stdout.decode()
                returncode = proc.returncode

                if require_return_code is not None:
                    if require_return_code != returncode:
                        # We need a specific code we didn't get, try again
                        attempts = attempts - 1
                        if attempts < 1:
                            p("}}rnInvalid return code(" + str(returncode) + ")! Giving up!}}xx\n" + out)
                            return ret
                        else:
                            p("}}ynInvalid return code(" + str(returncode) + "), trying again...}}xx\n" + out)
                            continue

                # No exception - cmd succeded
                cmd_succeded = True
                ret = (returncode, out)
                
            except subprocess.TimeoutExpired as ex:
                ex = ex # make pylint ignore
                # If timeout expires, just re-run
                attempts = attempts - 1
                if attempts < 1:
                    p("}}rnError - Command timed out, Giving up!}}xx")
                    return ret
                else:
                    p("}}ynTimeout waiting for command, trying again...}}xx")
                    continue
            except Exception as ex:
                attempts = attempts - 1
                if attempts < 1:
                    p("}}rnUnkown Error - too many attempts, Giving up!}}xx", log_level=3)
                    return ret
                else:
                    p("}}ynCommand failed (" + cmd + "), trying again...}}xx", log_level=5)
                    continue
                
        return ret

    @staticmethod
    def git_clone_branch(branch=None):
        # Command that is run to start this function
        only_for = "git_clone"

        if branch is None:
            branch = util.get_param(2, None, only_for=only_for)
        if branch is None:
            branch = RegistrySettings.get_git_branch()

        smc_url = RegistrySettings.get_reg_value(value_name="smc_url", default="https://smc.ed")
        smc_git = smc_url.replace("https", "git").replace("http", "git")
        
        app_path = util.get_app_folder()

        # Make sure the folder exists
        ope_laptop_binaries_path = os.path.expandvars("%programdata%\\ope\\tmp\\ope_laptop_binaries")
        ope_services_path = os.path.expandvars("%programdata%\\ope\\Services")

        # Make sure the ope_laptop_binaries folder is removed so we can do a fresh clone
        try:
            shutil.rmtree(ope_laptop_binaries_path, ignore_errors=True)
        except Exception as ex:
            ex = ex # make pylint chill
            p("}}rbFatal error - couldn't remove %programdata%\\ope\\tmp\\ope_laptop_binaries folder")
            return False

        # Make sure the folder exists and is blank
        os.makedirs(ope_laptop_binaries_path, exist_ok=True)
        os.makedirs(ope_services_path, exist_ok=True)

        git_path = os.path.join(app_path, "rc", "bin", "git.exe")

        # Make sure folder is a git repo
        cmd = git_path + " init \"" + ope_laptop_binaries_path + "\""
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to init git repo!}}xx\n" + output)
            return False
                
        ope_origin = "https://github.com/operepo/ope_laptop_binaries.git"
        ope_smc_origin = smc_git + "/ope_laptop_binaries.git"

        # Clone the repo
        cmd = git_path + " clone --depth=1 --single-branch --branch " + branch + " " + ope_origin + " . "
        p("}}gnTrying to clone from online repo, may take several minutes...}}xx")
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            attempts=1, require_return_code=0, cmd_timeout=None)
        if returncode == -2:
            # Error running command?
            p("}}ynUnable to clone laptop binaries from online source (ope_origin)! Trying SMC server.}}xx\n" + output)
            
            # Try from ope_smc_origin
            cmd = git_path + " clone --depth=1 --single-branch --branch " + branch + " " + ope_smc_origin + " . "
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
                attempts=1, require_return_code=0, cmd_timeout=None)
            if returncode == -2:
                # Error running command?
                p("}}rbError - Unable to clone laptop binaries from SMC server (ope_smc_origin)!}}xx\n" + output)
                return False
        
        # Add the origins to this git repo
        cmds = [
            git_path + " remote remove ope_origin",
            git_path + " remote remove ope_smc_origin",
            git_path + " remote add ope_origin " + ope_origin,
            git_path + " remote add ope_smc_origin " + ope_smc_origin
        ]

        for cmd in cmds:
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path)
            if returncode == -2:
                # Error running command?
                p("}}rbError - Unable to update remote locations!}}xx\n" + output)
                return False
       
        cmd = git_path + " rev-parse HEAD"
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to get the git revision ID!}}xx\n" + output)
            return False
        git_revision = output.strip()
        
        # Return the current git revision
        return git_revision

    @staticmethod
    def git_pull_branch(branch=None, binaries_path=None):

        # Command that is run to start this function
        only_for = "git_pull"

        if branch is None:
            branch = util.get_param(2, None, only_for=only_for)
        if branch is None:
            branch = RegistrySettings.get_git_branch()
        
        if binaries_path is None:
            binaries_path = util.get_param(3, None, only_for=only_for)
        if binaries_path is None:
            binaries_path = "%programdata%\\ope\\tmp\\ope_laptop_binaries"

        smc_url = RegistrySettings.get_reg_value(value_name="smc_url", default="https://smc.ed")
        smc_git = smc_url.replace("https", "git").replace("http", "git")
        
        # Make sure we remove any extra "s that can be stuck on
        binaries_path = binaries_path.strip('"')
        binaries_path = binaries_path.strip("'")
        
        app_path = util.get_app_folder()

        # Make sure the folder exists
        ope_laptop_binaries_path = os.path.abspath(os.path.expandvars(binaries_path)).replace("\"", "")
        ope_services_path = os.path.expandvars("%programdata%\\ope\\Services")
        p(ope_laptop_binaries_path, log_level=4)
        
        os.makedirs(ope_laptop_binaries_path, exist_ok=True)
        os.makedirs(ope_services_path, exist_ok=True)

        git_path = os.path.join(app_path, "rc", "bin", "git.exe")

        # Make sure folder is a git repo
        cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" init "
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to init git repo!}}xx\n" + output)
            return False

        # Remove any lock files that are old
        git_folder = os.path.join(ope_laptop_binaries_path, ".git")
        if os.path.exists(git_folder):
            # Get lock files.
            import glob
            file_list = glob.glob(git_folder + "/**/*.lock", recursive=True)
            for f in file_list:
                if os.path.isfile(f):
                    # Get the modified date
                    m_time = datetime.datetime.fromtimestamp(os.stat(f).st_mtime)
                    td = datetime.timedelta(minutes=5)  # Find files older then this
                    if m_time < datetime.datetime.now() - td:
                        # Older file...
                        p("}}ybRemoving old lock file:}}xx " + f)
                        os.unlink(f)
                
        # Add the origins to this git repo
        cmds = [
            git_path + " -C \"" + ope_laptop_binaries_path + "\" remote remove ope_origin",
            git_path + " -C \"" + ope_laptop_binaries_path + "\" remote remove ope_smc_origin",
            git_path + " -C \"" + ope_laptop_binaries_path + "\" remote add ope_origin https://github.com/operepo/ope_laptop_binaries.git",
            git_path + " -C \"" + ope_laptop_binaries_path + "\" remote add ope_smc_origin " + smc_git + "/ope_laptop_binaries.git"
        ]

        for cmd in cmds:
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path)
            p(str(output), log_level=4)
            if returncode == -2:
                # Error running command?
                p("}}rbError - Unable to update remote locations!}}xx\n" + output)
                return False
            
        # Do a fetch of the branch we want
        # - use -uf to update head and force fetch
        git_origin = "ope_origin"
        cmd = git_path +  " -C \"" + ope_laptop_binaries_path + "\" fetch --depth=1 -uf ope_origin " + branch + ":" + branch
        p("}}gnTrying to fetch from online repo, may take several minutes...}}xx")
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            attempts=1, require_return_code=0, cmd_timeout=None)
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            attempts=1, require_return_code=0, cmd_timeout=None)
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            attempts=1, require_return_code=0, cmd_timeout=None)
        if returncode == -2:
            # Error running command?
            p("}}ynUnable to fetch laptop binaries from online source (ope_origin)! Trying SMC server.}}xx\n" + output)
            
            # Try from ope_smc_origin
            git_origin = "ope_smc_origin"
            cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" fetch --depth=1 -uf ope_smc_origin " + branch
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
                attempts=1, require_return_code=0, cmd_timeout=None)
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
                attempts=1, require_return_code=0, cmd_timeout=None)
            returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
                attempts=1, require_return_code=0, cmd_timeout=None)
            if returncode == -2:
                # Error running command?
                p("}}rbError - Unable to fetch laptop binaries from SMC server (ope_smc_origin)!}}xx\n" + output)
                return False

        # Cleanup the folder prior to checkout
        # Make sure we don't have any changes in the folder
        # -f force, -d , -x remove ignore files too
        # cmds = [
        #     git_path + " -C \"" + ope_laptop_binaries_path + "\" checkout *",           # clear local changes since last commit
        #     git_path + " -C \"" + ope_laptop_binaries_path + "\" reset --hard HEAD ",   # Reset to current head
        #     git_path + " -C \"" + ope_laptop_binaries_path + "\" clean -fdx ",          # Delete local changed files
        #     #git_path + " checkout -f " + branch 
        # ]
        # for cmd in cmds:
        #     returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
        #         attempts=3, cmd_timeout=120)
        #     p(str(output), log_level=4)
        #     if returncode == -2:
        #         # Error running command?
        #         p("}}rbError - Unable to cleanup repo folder!}}xx\n" + output)
        #         return False
        # Clear old branch - had an ope_origin/master branch shouldn't be there
        cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" branch -d " + git_origin + "/" + branch
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
                cmd_timeout=150)
        p(str(output), log_level=4)
        # if returncode == -2:
        #     # Error running command?
        #     p("}}rbError - e_laptop_binaries folder and try again.}}xx\n" + output)
        #     return False


        # Checkout our changes
        # pull_options = " --autostash --depth=1 --force --no-rebase --allow-unrelated-histories"
        cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" checkout -f -B " + branch + " " + git_origin + "/" + branch
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0, cmd_timeout=150, attempts=2)
        p(str(output), log_level=4)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to checkout git changes! \nTry removing the %programdata%/ope/tmp/ope_laptop_binaries folder and try again.}}xx\n" + output)
            return False
        
        # Reset to head
        cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" reset --hard " + git_origin + "/" + branch
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0, cmd_timeout=150, attempts=2)
        p(str(output), log_level=4)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to checkout git changes! \nTry removing the %programdata%/ope/tmp/ope_laptop_binaries folder and try again.}}xx\n" + output)
            return False
        
        # Checkout our changes - again - just in case
        # pull_options = " --autostash --depth=1 --force --no-rebase --allow-unrelated-histories"
        cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" checkout -f -B " + branch + " " + git_origin + "/" + branch
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0, cmd_timeout=150, attempts=2)
        p(str(output), log_level=4)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to checkout git changes! \nTry removing the %programdata%/ope/tmp/ope_laptop_binaries folder and try again.}}xx\n" + output)
            return False

        # Get the revision id of this repo
        p("}}gnChecking versions...}}xx")
        cmd = git_path + " -C \"" + ope_laptop_binaries_path + "\" rev-parse HEAD"
        returncode, output = ProcessManagement.run_cmd(cmd, cwd=ope_laptop_binaries_path,
            require_return_code=0)
        p(str(output), log_level=4)
        if returncode == -2:
            # Error running command?
            p("}}rbError - Unable to get the git revision ID!}}xx\n" + output)
            return False
        git_revision = output.strip()
        p("}}ynGit Revision: " + str(git_revision) + "}}xx", log_level=3)
        
        # Get the revision id of the currently installed files
        # current_revision = "<not set>"
        # try:
        #     revision_file = open(os.path.join(ope_services_path, "git_revision.txt"))
        #     current_revision = revision_file.read()
        #     current_revision = current_revision.strip()
        #     revision_file.close()
        # except Exception as ex:
        #     p("}}ynWarning - unable to open the git_revision.txt file! This will trigger an update.}}xx\n" + \
        #         str(ex), debug_level=2)

        return True



if __name__ == "__main__":
    # >> nul 2>&1
    long_running_cmd = os.path.expandvars("%programdata%\\ope\\tmp\\ope_laptop_binaries\\Services\\mgmt\\rc\\upgrade_ope.cmd >> %programdata%\\ope\\tmp\\log\\upgrade.log 2>&1")
    
    #ProcessManagement.run_detatched_cmd(long_running_cmd)
    ProcessManagement.run_process_as_user("cmd.exe", user_name="ray")

    p("exiting test.")

    