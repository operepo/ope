# NOTE - VENV Below specifies which python to use for this app - currently 3.6

import os
import sys
import shutil

project_name = "SyncApp"
main_file = "sync_gui.py"

os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"  # "glew" # "angle_sdl2"  # gl, glew, sdl2, angle_sdl2, mock
os.environ["KIVY_GRAPHICS"] = "gles"  # "gles"
os.environ["PATH"] = os.environ["PATH"] +\
                     ";C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86" + \
                     ";C:\\Python37-32\\Lib\\site-packages\\enchant" + \
                     ";c:\\Windows\\system32"
# os.environ["KIVY_GL_DEBUG"] = "1"
# os.environ["USE_SDL2"] = "1"
# os.environ["KIVY_WINDOW"] = "pygame"  # "sdl2" "pygame"
# os.environ["KIVY_IMAGE"] = "sdl2"  # img_tex, img_dds, img_sdl2, img_ffpyplayer, img_gif, img_pil
# os.environ["KIVY_TEXT"] = "sdl2"


BASE_FOLDER = os.path.dirname(__file__)
# VENV = os.path.join(BASE_FOLDER, "venv", "Scripts", "python.exe")
# VENV = "c:\\python27\\python.exe "
VENV = "c:\\python36-32\\python.exe "

print("USING SPEC FILE")
# print("python -m PyInstaller --noconfirm SyncApp.spec")
os.system(VENV + " -m PyInstaller --noconfirm {0}.spec".format(project_name))
exit()

print(os.getcwd())

# Copy in the assets we need
assets = [("SyncOPEApp.kv", "."), ("OfflineServerSettings.json", "."), ("OnlineServerSettings.json", "."),
          ("logo_icon.ico", "."), ("logo_icon.png", "."), ("GettingStarted.md", "."),
          ("version.json", "."), ]

# This should be done in the Analysis portion
# print("Copying Assets...")
# if os.path.isdir(os.path.join('dist', project_name)) is not True:
#     os.makedirs(os.path.join("dist", project_name))
# for a in assets:
#     shutil.copyfile(a, os.path.join("dist", project_name, a))


# == Build the app for windows using pyinstaller ==
# os.system("python -m PyInstaller --noconfirm --name {0} {1}".format(project_name, main_file))
os.system(VENV + " -m PyInstaller --noconfirm --name {0} --icon logo_icon.ico {1}".format(project_name, main_file))

options = []  # [ ('p', "C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86", 'OPTION'), ]

# Add imports to beginning of spec file
f = open("{0}.spec".format(project_name), "r")
lines = f.readlines()
f.close()
f = open("{0}.spec".format(project_name), "w")
f.write("from kivy.deps import sdl2, glew, angle\n")
# f.write("from kivy.deps import sdl2, glew\n")
for line in lines:
    #  Assets to add to the install folder
    if line.strip().startswith("datas=[]"):
        line = "             datas=" + str(assets) + ",\n"
    # Add the depends line below the a.datas, line
    if line.strip().startswith("a.datas,"):
        line += "               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + angle.dep_bins)],\n"
        # line += "               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],\n"
    if len(options) > 0:
        # Only add options if there are options to add
        print("ADJUSTING OPTIONS")
        if line.strip().startswith("a.scripts"):
            line += "               " + str(options) + ",\n"
    if line.strip().startswith("upx="):
        line = line.replace("True", "False")
    f.write(line)
f.close()


# Now rebuild with the adjusted spec file
os.system(VENV + " -m PyInstaller --noconfirm {0}.spec".format(project_name))

# Remove the manifest file (fixes opengl detection errors)
os.unlink(os.path.join("dist", project_name, project_name+".exe.manifest"))

# Move/Package the EXE files for easy download/install
# TODO
# Pyinstaller not copying all of the data folder properly, do it manually
# TODO - Copy C:\Python27\Lib\site-packages\kivy\data to ./kivy_install/data
# src_folder = os.path.join(VENV, "Lib", "site-packages", "kivy", "data")
# dest_folder = os.path.join(BASE_FOLDER, "dist", "SyncApp", "kivy_install", "data")
