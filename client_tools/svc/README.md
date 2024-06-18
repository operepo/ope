
# Build Instructions

Use nuitka for all but OPEService. Using python 3.11 for all builds (3.12 has issue with opeservice)
Nuitka doesn't work for services unless you pay for commercial packages.

.\nuitka_build.cmd (for mgmt) - copy over mgmt.dist folder
.\nuitka_lock_screen_widget_build.cmd - for lock screen widget - copy over lock_screen_widget.dist folder
.\nuitka_sshot_build.cmd - copy over sshot.dist folder

For OPEService - (use python 3)
python .\build_svc.py - copy over dist/opeservice folder




## PyInstaller - Custom Build
https://python.plainenglish.io/pyinstaller-exe-false-positive-trojan-virus-resolved-b33842bd3184
Need to do a custom build for pyinstaller due to antivirus issues.

After cloning - add variables to functions in bootloader/src/pyi_main.c 
Adding something like - int ope_custom=1; in each function is enough to change binary signatures so they don't trip antivirus as a known bad actor.


### Clone Pyinstaller

https://github.com/pyinstaller/pyinstaller 

Clone to c:\pyinstaller
cd c:\pyinstaller\bootloader

pip uninstall pyinstaller

Use chocolaty to install stuff as stated on pyinstaller page
https://pyinstaller.org/en/stable/bootloader-building.html

Switch back to python 311 (chocolaty installs py3.12 - remove from paths and re-open command prompts)

Set this flag to disable telemetry
setx VSCMD_SKIP_SENDTELEMETRY 1


In the bootloader folder - run waf...
python .\waf distclean all --target-arch=64bit

Install the built pyinstaller
cd c:\pyinstaller
pip install .
