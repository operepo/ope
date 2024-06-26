import os
import sys
import shutil

project_name = "mgmt"
main_file = "mgmt.py"

# If you get corrupted errors, use this
clean = " "  # " --clean "
debug = " --debug all " # --debug all
remove_spec_file = True

spec_file = project_name + ".spec"

# Don't wan't old spec files right now.
if remove_spec_file and os.path.exists(spec_file):
    os.unlink(spec_file)

# options = [ ('v', None, 'OPTION'), ('W ignore', None, 'OPTION') ]
# Put after exe=exe(...a.scripts, options)
#--noconsole
data_files = " --add-data logo_icon.ico;. --add-data rc;rc --add-data mgmt.version;. " + \
    " --add-data install_service.cmd;. "
hidden_imports = "--hidden-import sip --hidden-import win32timezone --hidden-import simplejson "
build_params = "python -m PyInstaller " + clean + debug + \
    hidden_imports + \
    " --noupx " + \
    data_files + " --noconfirm --icon logo_icon.ico "
# == Build the app for windows using pyinstaller ==

if os.path.exists(spec_file):
    # Build using the existing spec file
    print("Building w existing spec file...")
    os.system(build_params + " {0}.spec".format(project_name))
else:
    print("Building fresh copy...")
    os.system(build_params + " --name {0} {1}".format(project_name, main_file))

print("Done!")