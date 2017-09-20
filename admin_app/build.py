import os
import sys

project_name = "SyncApp"
main_file = "sync_gui.py"

# == Build the app for windows using pyinstaller ==
#os.system("python -m PyInstaller --noconfirm --name {0} {1}".format(project_name, main_file))
os.system("python -m PyInstaller --noconfirm --name {0} --icon logo_icon.ico {1}".format(project_name, main_file))

# Add imports to beginning of spec file
f = open("{0}.spec".format(project_name), "r")
lines = f.readlines()
f.close()
f = open("{0}.spec".format(project_name), "w")
f.write("from kivy.deps import sdl2, glew\n")
for line in lines:
    # Add the depends line below the a.datas, line
    if line.strip().startswith("a.datas,"):
        line += "               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],\n"
    f.write(line)
f.close()


# No rebuild with the adjusted spec file
os.system("python -m PyInstaller --noconfirm {0}.spec".format(project_name))

