import sys
import os
from win32com.shell import shellcon, shell

# Should be programdata files folder
ROOT_FOLDER = os.path.join(
    shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0), "ope")
    
TMP_FOLDER = os.path.join(ROOT_FOLDER, "tmp")
LOG_FOLDER = os.path.join(TMP_FOLDER, "log")
SCREEN_SHOTS_FOLDER = os.path.join(TMP_FOLDER, "screen_shots")
GIT_FOLDER = os.path.join(TMP_FOLDER, "ope_laptop_binaries")
BINARIES_FOLDER = os.path.join(ROOT_FOLDER, "Services")
STUDENT_DATA_FOLDER = os.path.join(ROOT_FOLDER, "student_data")
LOCK_SCREEN_WIDGET_FOLDER = os.path.join(TMP_FOLDER, "lock_screen_widget")
CONFIG_FOLDER = os.path.join(ROOT_FOLDER, "config")
QML_CACHE_FOLDER = os.path.join(TMP_FOLDER, "qmlcache")

# The base function called
CMD_FUNCTION = ""

global APP_FOLDER
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
        # Add this folder to the os path so that resources can be found more reliably
        #text_dir = os.path.join(APP_FOLDER, "kivy\\core\\text")
        #os.environ["PATH"] = os.environ["PATH"] + ";" + ret + ";" + text_dir
        #print("-- ADJUSTING SYS PATH -- " + os.environ["PATH"])

    else:
        ret = APP_FOLDER
    return ret

get_app_folder()

def get_dict_value(source_dict, key_name, default=""):
    ret = default
    if key_name in source_dict:
        ret = source_dict[key_name]
    return ret

def pop_force_flag(only_for=None):
    # See if the -f is present in the params and remove it if it is.
    ret = False

    global CMD_FUNCTION

    # only_for - just return param if it is the root call, otherwise False
    if not only_for is None:
        if CMD_FUNCTION != only_for:
            return ret

    for i in range(len(sys.argv)):
        p = sys.argv[i]
        if p.lower() == "-f":
            #print("Found force flag!")
            ret = True
            sys.argv.remove(p)
            break

    return ret
def get_param(param_index=1, default_value="", only_for=None):
    # Get the requested parameter or default value if non existent
    ret = default_value

    global CMD_FUNCTION

    # only_for - just return param if it is the root call
    if not only_for is None:
        if CMD_FUNCTION != only_for:
            return ret

    if len(sys.argv) >=param_index + 1:
        ret = sys.argv[param_index]
    
    return ret

def test_params():

    force_on = pop_force_flag()
    print("Force: " + str(force_on))
    print("Params:")
    for i in range(len(sys.argv)):
        print("Param " + str(i) + "=>" + str(sys.argv[i]))
    print(len(sys.argv))
    return

if __name__ == "__main__":
    # Test the params
    test_params()