# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com, sys
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass


from distutils.core import setup
import py2exe
from glob import glob
import sys
import os
import shutil

DESCRIPTION = 'OPE Service - Admin service for OPE project'
NAME = 'Ope Service'
INCLUDES = "win32com,win32service,win32serviceutil,win32event,win32api"
OPTIMIZE = "2"

sys.path.insert(0,os.getcwd())
 
def getFiles(dir):
    """
    Retorna una tupla de tuplas del directorio
    """
    # dig looking for files
    a= os.walk(dir)
    b = True
    filenames = []
 
    while (b):
        try:
            (dirpath, dirnames, files) = a.next()
            filenames.append([dirpath, tuple(files)])
        except:
            b = False
    return filenames

buildservice = True
if '--no-service' in sys.argv[1:]:
    buildservice = False
    sys.argv = [k for k in sys.argv if k != '--no-service']
    print sys.argv

sys.path.append("Microsoft.VC90.CRT")

# To send msvcrt dll files
data_files = [("Microsoft.VC90.CRT", glob(r'Microsoft.VC90.CRT.9.0.3\*.*'))]


class Target:
    def __init__(self,**kw):
            self.__dict__.update(kw)
            self.version        = "1.00.00"
            self.compay_name    = "OPE"
            self.copyright      = "(c) 2017, OPE"
            self.name           = NAME
            self.description    = DESCRIPTION
 
my_com_server_target = Target(
        description    = DESCRIPTION,
        service = ["OPEService"],
        modules = ["OPEService"],
        create_exe = True,
        create_dll = True)

        
if not buildservice:
    print 'Compiling windows executable...'
    setup(
        name = NAME ,
        description = DESCRIPTION,
        version = '1.00.00',
        console = ['svc.py'],
        zipfile=None,
        options = {
                "py2exe":{"packages":"encodings",
                    "includes":INCLUDES,
                    "optimize": OPTIMIZE
                    },
                },
    )
else:
    print 'Compiling windows service...'
    setup(
        name = NAME,
        description = DESCRIPTION,
        version = '1.00.00',
        service = [{'modules':["OPEService"], 'cmdline':'pywin32'}],
        zipfile=None,
        options = {
                "py2exe":{"packages":"encodings",
                    "includes":INCLUDES,
                    "optimize": OPTIMIZE
                    },
                },
    )        
        
        
# opeservice = Target(
    # used for the versioninfo resource
    # description = "OPE Service",
    # what to build. For a service, the module name (not the
    # filename) must be specified!
    # modules = ["svc"],
    # cmdline_style='pywin32',
    # )

    
# setup(
    
    # service=['svc.py'],
    # )
# setup(
    # version = "0.0.1",
    # description = "OPEService",
    # name = "OPEService",
    # modules = ["MyService"],
    # cmdline_style='pywin32',
    # options={ "py2exe": {
        # "unbuffered": True,
        # "bundle_files": 3,
        # "packages": ["Crypto",],
        # }},
    # console=['install_updates.py', 'update_dns.py', 'change_all_dns.py', 'sys_ping.py', 'long_running_test.py', 'install_wamap_videos.py', 'flush_redis.py', 'install_pmox_repository.py', 'reset_ceph.py', 'sync_time.py', 'ceph_status.py', 'adjust_log_rotate_pmox.py'],
    # data_files=data_files,
# )





