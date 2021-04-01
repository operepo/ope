import os
import sys
import shutil

project_name = "lock_screen_widget"
main_file = "lock_screen_widget.py"

# If you get corrupted errors, use this
clean = " "  # " --clean "
remove_spec_file = False

spec_file = project_name + ".spec"


#--noconsole
#--hidden-import pkg_resources.py2_warn
#--hidden-import sip 
build_params = "python -m PyInstaller " + clean + \
    " --noconsole --noupx --add-data logo_icon.ico;. " + \
    " --add-data STENCIL.TTF;. " + \
    " --noconfirm --icon logo_icon.ico "
# == Build the app for windows using pyinstaller ==

if os.path.exists(spec_file):
    # Build using the existing spec file
    print("Building w existing spec file...")
    os.system(build_params + " {0}.spec".format(project_name))
else:
    print("Building fresh copy...")
    os.system(build_params + " --name {0} {1}".format(project_name, main_file))

print("Done!")