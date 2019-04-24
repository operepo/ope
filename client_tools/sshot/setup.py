#ModuleFinder can't handle runtime changes to __path__, but win32com uses them
# try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    # try:
        # import py2exe.mf as modulefinder
    # except ImportError:
        # import modulefinder
    # import win32com, sys
    # for p in win32com.__path__[1:]:
        # modulefinder.AddPackagePath("win32com", p)
    # for extra in ["win32com.shell"]: #,"win32com.mapi"
        # __import__(extra)
        # m = sys.modules[extra]
        # for p in m.__path__[1:]:
            # modulefinder.AddPackagePath(extra, p)
# except ImportError:
    #no build path setup, no worries.
    # pass


from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import shutil

DESCRIPTION = 'OPE Screen Shot - Used to grab screen shots of the current desktop'
NAME = 'OpeSShot'
VERSION = '1.00.01'
INCLUDES = "win32com"  # "win32com,win32service,win32serviceutil,win32event,win32api"
OPTIMIZE = "2"

sys.path.insert(0, os.getcwd())


def getFiles(dir):
    """
    Retorna una tupla de tuplas del directorio
    """
    # dig looking for files
    a = os.walk(dir)
    b = True
    filenames = []
 
    while b:
        try:
            (dirpath, dirnames, files) = a.next()
            filenames.append([dirpath, tuple(files)])
        except:
            b = False
    return filenames


sys.path.append("Microsoft.VC90.CRT")

# To send msvcrt dll files
data_files = [("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT.9.0.3\*.*'))]
        
print('Compiling windows executable...')
setup(
    name=NAME,
    description=DESCRIPTION,
    version=VERSION,
    windows=['sshot.py'],  # Use this if you want a win app w no console - we DO (silent execution)
    # console=['sshot.py'],  # Use this if you want a console to appear - we do NOT
    zipfile=None,
    options={
            "py2exe": {"unbuffered": True, "packages": "encodings",
                       "includes": INCLUDES,
                       "optimize": OPTIMIZE
                       },
            },
    data_files=data_files
)
