import sys
import os
from win32com.shell import shellcon, shell

# Should be programdata files folder
ROOT_FOLDER = os.path.join(
    shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
    
TMP_FOLDER = os.path.join(ROOT_FOLDER, "tmp")
LOG_FOLDER = os.path.join(TMP_FOLDER, "log")
SCREEN_SHOTS_FOLDER = os.path.join(TMP_FOLDER, "screen_shots")
GIT_FOLDER = os.path.join(ROOT_FOLDER, "ope_laptop_binaries")
BINARIES_FOLDER = os.path.join(ROOT_FOLDER, "Services")
STUDENT_DATA_FOLDER = os.path.join(ROOT_FOLDER, "student_data")



def get_param(param_index=1, default_value=""):
    # Get the requested parameter or default value if non existent
    ret = default_value

    if len(sys.argv) >=param_index + 1:
        ret = sys.argv[param_index]
    
    return ret