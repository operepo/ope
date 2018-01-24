import os
import sys
import shutil

project_name = "SyncApp"
main_file = "sync_gui.py"

BASE_FOLDER = os.path.dirname(__file__)
#VENV = os.path.join(BASE_FOLDER, "venv", "Scripts", "python.exe")
VENV = "c:\python27\python.exe "
print(os.getcwd())
# == Build the app for windows using pyinstaller ==
# os.system("python -m PyInstaller --noconfirm --name {0} {1}".format(project_name, main_file))
os.system(VENV + " -m PyInstaller --noconfirm --name {0} --icon logo_icon.ico {1}".format(project_name, main_file))

# Add imports to beginning of spec file
f = open("{0}.spec".format(project_name), "r")
lines = f.readlines()
f.close()
f = open("{0}.spec".format(project_name), "w")
#f.write("from kivy.deps import sdl2, glew, angle\n")
f.write("from kivy.deps import sdl2, glew\n")
for line in lines:
    # Add the depends line below the a.datas, line
    if line.strip().startswith("a.datas,"):
        # line += "               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + angle.dep_bins)],\n"
        line += "               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],\n"
    f.write(line)
f.close()


# Now rebuild with the adjusted spec file
os.system(VENV + " -m PyInstaller --noconfirm {0}.spec".format(project_name))

# Copy in the assets we need
assets = ["SyncOPEApp.kv", "OfflineServerSettings.json", "OnlineServerSettings.json", "logo_icon.ico", "logo_icon.png",
          "GettingStarted.md"]
for a in assets:
    shutil.copyfile(a, os.path.join("dist", project_name, a))

# Remove the manifest file (fixes opengl detection errors)
os.unlink(os.path.join("dist", project_name, project_name+".exe.manifest"))

# Move/Package the EXE files for easy download/install
# TODO
# Pyinstaller not copying all of the data folder properly, do it manually
# TODO - Copy C:\Python27\Lib\site-packages\kivy\data to ./kivy_install/data
# src_folder = os.path.join(VENV, "Lib", "site-packages", "kivy", "data")
# dest_folder = os.path.join(BASE_FOLDER, "dist", "SyncApp", "kivy_install", "data")
