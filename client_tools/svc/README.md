
# Build Instructions

Use Python3 w pyinstaller

Build using by using the makeexe.cmd file - final app is in dist folder.

Copy dist folder to laptop binaries under sshot folder to release.



## PyInstaller - Custom Build
https://python.plainenglish.io/pyinstaller-exe-false-positive-trojan-virus-resolved-b33842bd3184
Need to do a custom build for pyinstaller due to antivirus issues.

### Clone Pyinstaller - GCC

https://github.com/pyinstaller/pyinstaller 

Clone to c:\pyinstaller  choose v4 branch
Checkout current version/tag (e.g. 4.10)

Open Command Prompt as admin
cd C:\Qt\6.2.0\mingw81_64\bin
qtenv2.bat

cd c:\pyinstaller\bootloader

pip uninstall pyinstaller
python ./waf distclean all --target-arch=64bit --gcc
cd ..
python setup.py install

In OPE code folder, delete __pycache__, dist, build folders
Run makeexe.cmd file to build
Test with virustotal.com



### Clone Pyinstaller - MSVC

https://github.com/pyinstaller/pyinstaller 

Clone to c:\pyinstaller  choose v4 branch
Checkout current version/tag (e.g. 4.10)

Open MSVC Command prompt (x64 right now) and cd to c:\pyinstaller\bootloader

pip uninstall pyinstaller
python ./waf distclean all --target-arch=64bit
cd ..
python setup.py install

In OPE code folder, delete __pycache__, dist, build folders
Run makeexe.cmd file to build
Test with virustotal.com
