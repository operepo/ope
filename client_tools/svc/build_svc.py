import os
import sys
import shutil

project_name = "OPEService"
main_file = "OPEService.py"


spec_file = project_name + ".spec"

# Don't wan't old spec files right now.
if os.path.exists(spec_file):
    os.unlink(spec_file)
#--noconsole
CUSTOM_EVENT_LOG_DLL=" --add-binary mgmt_EventLogMessages.dll;. "
build_params = "python -m PyInstaller --hidden-import sip --hidden-import win32timezone --noupx " + \
    " --add-binary logo_icon.ico;. " + CUSTOM_EVENT_LOG_DLL + " --noconfirm --icon logo_icon.ico "
# == Build the app for windows using pyinstaller ==

if os.path.exists(spec_file):
    # Build using the existing spec file
    print("Building w existing spec file...")
    os.system(build_params + " {0}.spec".format(project_name))
else:
    print("Building fresh copy...")
    os.system(build_params + " --name {0} {1}".format(project_name, main_file))

print("Done!")