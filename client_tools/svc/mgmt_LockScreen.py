# Needed for running as alternate user
import win32ts
import win32security
import win32con
import win32process
import win32api
import win32profile

# For startupinfoex
import enum
from ctypes.wintypes import *
from ctypes import *
kernel32 = WinDLL('kernel32',  use_last_error=True)
advapi32 = WinDLL('advapi32',  use_last_error=True)
shell32  = WinDLL('shell32',   use_last_error=True)
psapi    = WinDLL('psapi.dll', use_last_error=True)
userenv = ctypes.WinDLL('userenv', use_last_error=True)

import subprocess
import sys
import os
import time
import psutil
import traceback

from color import p

import util
from mgmt_UserAccounts import UserAccounts
from mgmt_ProcessManagement import ProcessManagement
from mgmt_Computer import Computer

### Structs - for use with CTYpes (startupinfoex)
#Source - https://gist.github.com/makelariss/acc7b1b4589e51905a93db46ac5f81b2
                                                                # https://docs.python.org/2/library/ctypes.html#structures-and-unions
                                                                
# An LUID is a 64-bit value guaranteed to be unique only on the system on which it was generated
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379261(v=vs.85).aspx
class LUID(Structure):                                         # typedef struct _LUID
     _fields_ = [				               # {
		('LowPart', DWORD),                            # DWORD LowPart;
                ('HighPart', LONG)                             # LONG  HighPart;
	        ]			                       # }

# The LUID_AND_ATTRIBUTES structure represents a locally unique identifier (LUID) and its attributes.
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379263(v=vs.85).aspx
class LUID_AND_ATTRIBUTES(Structure):                          # typedef struct _LUID_AND_ATTRIBUTES
     _fields_ = [                                              # {
		('Luid',      LUID), 	  	 	       # LUID  Luid;
                ('Attributes',DWORD)			       # DWORD Attributes;
 	        ]					       # }

PSID = c_void_p
# The SID_AND_ATTRIBUTES structure represents a security identifier (SID) and its attributes. SIDs are used to uniquely identify users or groups
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379595(v=vs.85).aspx
class SID_AND_ATTRIBUTES(Structure):                           # typedef struct _SID_AND_ATTRIBUTES
    _fields_ = [                                               # {
               ('Sid',         PSID),                          # PSID  Sid;
               ('Attributes',  DWORD)                          # DWORD Attributes;
               ]                                               # }


# The TOKEN_PRIVILEGES structure contains information about a set of privileges for an access token.
							        # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379630(v=vs.85).aspx
class TOKEN_PRIVILEGES(Structure):      		       # typedef struct _TOKEN_PRIVILEGES
     _fields_ = [                                              # {
		('PrivilegeCount',  DWORD),		       # DWORD               PrivilegeCount;
                ('Privileges',      LUID_AND_ATTRIBUTES * 512) # LUID_AND_ATTRIBUTES Privileges[ANYSIZE_ARRAY];
	        ]			                       # }

                                                                # https://docs.python.org/3/library/ctypes.html#specifying-the-required-argument-types-function-prototypes
class c_enum(enum.IntEnum):                                    # A ctypes-compatible IntEnum superclass that implements the class method
    @classmethod                                               # https://docs.python.org/3/library/functions.html#classmethod
    def from_param(cls, obj):                                  # Define the class method `from_param`.
        return c_int(cls(obj))                                 # The obj argument to the from_param method is the object instance, in this case the enumerated value itself. Any Enum with an integer value can be directly cast to int. TokenElevation -> TOKEN_INFORMATION_CLASS.TokenElevation

# The TOKEN_INFORMATION_CLASS enumeration contains values that specify the type of information being assigned to or retrieved from an access token
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379626(v=vs.85).aspx
class TOKEN_INFORMATION_CLASS(c_enum):                         # typedef enum _TOKEN_INFORMATION_CLASS {
#spoilers    TokenUser       = 1                               # TokenUser       The buffer receives a TOKEN_USER structure that contains the user account of the token
#spoilers    TokenGroups     = 2                               # TokenGroups     The buffer receives a TOKEN_GROUPS structure that contains the group accounts associated with the token
#spoilers    TokenPrivileges = 3                               # TokenPrivileges The buffer receives a TOKEN_PRIVILEGES structure that contains the privileges of the token
     TokenElevation = 20                                       # TokenElevationType The buffer receives a TOKEN_ELEVATION_TYPE value that specifies the elevation level of the token.


# DWORD_PTR = POINTER(DWORD)
SIZE_T    = c_size_t
PVOID     = c_void_p
# This structure stores the value for each attribute
                                                                # http://www.rohitab.com/discuss/topic/38601-proc-thread-attribute-list-structure-documentation/
class PROC_THREAD_ATTRIBUTE_ENTRY(Structure):                  # typedef struct _PROC_THREAD_ATTRIBUTE_ENTRY
    _fields_ = [                                               # {
               ("Attribute",     DWORD),                       # DWORD_PTR   Attribute;  // PROC_THREAD_ATTRIBUTE_xxx # https://msdn.microsoft.com/en-us/library/windows/desktop/ms686880(v=vs.85).aspx
               ("cbSize",       SIZE_T),                       # SIZE_T      cbSize;
               ("lpValue",       PVOID)                        # PVOID       lpValue
               ]                                               # }

PULONG = POINTER(ULONG)
# This structure contains a list of attributes that have been added using UpdateProcThreadAttribute
                                                                # http://www.rohitab.com/discuss/topic/38601-proc-thread-attribute-list-structure-documentation/
class PROC_THREAD_ATTRIBUTE_LIST(Structure):                   # typedef struct _PROC_THREAD_ATTRIBUTE_LIST
    _fields_ = [                                               # {
               ("dwFlags", DWORD),                             # DWORD                      dwFlags;
               ("Size",    ULONG),                             # ULONG                      Size;
               ("Count",   ULONG),                             # ULONG                      Count;
               ("Reserved",ULONG),                             # ULONG                      Reserved;
               ("Unknown", PULONG),                            # PULONG                     Unkown;
               ("Entries", PROC_THREAD_ATTRIBUTE_ENTRY * 1)    # PROC_THREAD_ATTRIBUTE_LIST Entries[ANYSIZE_ARRAY]
               ]                                               # }

LPVOID = PVOID
LPTSTR = c_void_p
LPBYTE = c_char_p
# Specifies the window station, desktop, standard handles, and appearance of the main window for a process at creation time.
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/ms686331(v=vs.85).aspx
class STARTUPINFO(Structure):                                  # typedef struct _STARTUPINFO
    _fields_ = [                                               # {
               ('cb',               DWORD),                    # DWORD  cb;
               ('lpReserved',       LPWSTR),                   # LPTSTR lpReserved;
               ('lpDesktop',        LPWSTR), #LPTSTR),                   # LPTSTR lpDesktop;
               ('lpTitle',          LPWSTR), #LPTSTR),                   # LPTSTR lpTitle;
               ('dwX',              DWORD),                    # DWORD  dwX;
               ('dwY',              DWORD),                    # DWORD  dwY;
               ('dwXSize',          DWORD),                    # DWORD  dwXSize;
               ('dwYSize',          DWORD),                    # DWORD  dwYSize;
               ('dwXCountChars',    DWORD),                    # DWORD  dwXCountChars;
               ('dwYCountChars',    DWORD),                    # DWORD  dwYCountChars;
               ('dwFillAttribute',  DWORD),                    # DWORD  dwFillAttribute;
               ('dwFlags',          DWORD),                    # DWORD  dwFlags;
               ('wShowWindow',       WORD),                    # WORD   wShowWindow;
               ('cbReserved2',       WORD),                    # WORD   cbReserved2;
               ('lpReserved2',     LPBYTE),                    # LPBYTE lpReserved2;
               ('hStdInput',       HANDLE),                    # HANDLE hStdInput;
               ('hStdOutput',      HANDLE),                    # HANDLE hStdOutput;
               ('hStdError',       HANDLE)                     # HANDLE hStdError;
               ]                                               # }

PPROC_THREAD_ATTRIBUTE_LIST = POINTER(PROC_THREAD_ATTRIBUTE_LIST)
# Specifies the window station, desktop, standard handles, and attributes for a new process. It is used with the CreateProcess and CreateProcessAsUser functionsself.
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/ms686329(v=vs.85).aspx
class STARTUPINFOEX(Structure):                                #   typedef struct _STARTUPINFOEX
    _fields_ = [                                               #   {
               ('StartupInfo',     STARTUPINFO),               #   STARTUPINFO                 StartupInfo;
               ('lpAttributeList', LPVOID),                    # PPROC_THREAD_ATTRIBUTE_LIST lpAttributeList; # lpStartupInfo = STARTUPINFOEX(); lpStartupInfo.lpAttributeList = addressof(AttributeList)
               ]                                               # }

# Contains information about a newly created process and its primary thread. It is used with the CreateProcess, CreateProcessAsUser, CreateProcessWithLogonW, or CreateProcessWithTokenW function.
                                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/ms684873(v=vs.85).aspx
class PROCESS_INFORMATION(Structure):                          # typedef struct _PROCESS_INFORMATION
    _fields_ = [                                               # {
               ("hProcess",    HANDLE),                        # HANDLE hProcess;
               ("hThread",     HANDLE),                        # HANDLE hThread;
               ("dwProcessId",  DWORD),                        # DWORD  dwProcessId;
               ("dwThreadId",   DWORD)                         # DWORD  dwThreadId;
               ]                                               # }


# Privilege constants                                                # https://msdn.microsoft.com/en-us/library/windows/desktop/bb530716(v=vs.85).aspx
SE_ASSIGNPRIMARYTOKEN_NAME     = "SeAssignPrimaryTokenPrivilege"    # Replace a process-level token
SE_AUDIT_NAME                  = "SeAuditPrivilege"                 # Generate security audits
SE_BACKUP_NAME                 = "SeBackupPrivilege"                # Back up files and directories
SE_CHANGE_NOTIFY_NAME          = "SeChangeNotifyPrivilege"	    # Bypass traverse checking
SE_CREATE_GLOBAL_NAME          = "SeCreateGlobalPrivilege"          # Create global objects
SE_CREATE_PAGEFILE_NAME        = "SeCreatePagefilePrivilege"        # Create a pagefile
SE_CREATE_PERMANENT_NAME       = "SeCreatePermanentPrivilege"       # Create permanent shared objects
SE_CREATE_SYMBOLIC_LINK_NAME   = "SeCreateSymbolicLinkPrivilege"    # Create symbolic links
SE_CREATE_TOKEN_NAME           = "SeCreateTokenPrivilege"           # Create a token object
SE_DEBUG_NAME                  = "SeDebugPrivilege"                 # Debug programs | * Malwares <3 this one *
SE_ENABLE_DELEGATION_NAME      = "SeEnableDelegationPrivilege"      # Enable computer and user accounts to be trusted for delegation
SE_IMPERSONATE_NAME            = "SeImpersonatePrivilege"           # Impersonate a client after authentication
SE_INC_BASE_PRIORITY_NAME      = "SeIncreaseBasePriorityPrivilege"  # Increase scheduling priority
SE_INCREASE_QUOTA_NAME         = "SeIncreaseQuotaPrivilege"         # Adjust memory quotas for a process
SE_INC_WORKING_SET_NAME        = "SeIncreaseWorkingSetPrivilege"    # Increase a process working set
SE_LOAD_DRIVER_NAME            = "SeLoadDriverPrivilege"            # Load and unload device drivers | DKOM, rootkits, EPROCESS for process hiding
SE_LOCK_MEMORY_NAME            = "SeLockMemoryPrivilege"            # Lock pages in memory
SE_MACHINE_ACCOUNT_NAME        = "SeMachineAccountPrivilege"        # Add workstations to domain
SE_MANAGE_VOLUME_NAME          = "SeManageVolumePrivilege"          # Manage the files on a volume
SE_PROF_SINGLE_PROCESS_NAME    = "SeProfileSingleProcessPrivilege"  # Profile single process
SE_RELABEL_NAME                = "SeRelabelPrivilege"               # Modify an object label
SE_REMOTE_SHUTDOWN_NAME        = "SeRemoteShutdownPrivilege"        # Force shutdown from a remote system
SE_RESTORE_NAME                = "SeRestorePrivilege"               # Restore files and directories
SE_SECURITY_NAME               = "SeSecurityPrivilege"              # Manage auditing and security log
SE_SHUTDOWN_NAME               = "SeShutdownPrivilege"              # Shut down the system
SE_SYNC_AGENT_NAME             = "SeSyncAgentPrivilege"             # Synchronize directory service data
SE_SYSTEM_ENVIRONMENT_NAME     = "SeSystemEnvironmentPrivilege"     # Modify firmware environment values
SE_SYSTEM_PROFILE_NAME         = "SeSystemProfilePrivilege"         # Profile system performance
SE_SYSTEMTIME_NAME             = "SeSystemtimePrivilege"            # Change the system time
SE_TAKE_OWNERSHIP_NAME         = "SeTakeOwnershipPrivilege"         # Take ownership of files or other objects
SE_TCB_NAME                    = "SeTcbPrivilege"                   # Act as part of the operating system
SE_TIME_ZONE_NAME              = "SeTimeZonePrivilege"              # Change the time zone
SE_TRUSTED_CREDMAN_ACCESS_NAME = "SeTrustedCredManAccessPrivilege"  # Access Credential Manager as a trusted caller
SE_UNDOCK_NAME                 = "SeUndockPrivilege"                # Remove computer from docking station
SE_UNSOLICITED_INPUT_NAME      = "SeUnsolicitedInputPrivilege"      # "Required to read unsolicited input from a terminal device"



# A pointer to a TOKEN_PRIVILEGES structure that specifies an array of privileges and their attributes.
# NewState [in, optional]                       #  https://msdn.microsoft.com/en-us/library/windows/desktop/aa375202(v=vs.85).aspx
SE_PRIVILEGE_ENABLED_BY_DEFAULT     = 0x00000001
SE_PRIVILEGE_ENABLED                = 0x00000002   # The function enables the privilege
SE_PRIVILEGE_REMOVED                = 0x00000004   # The privilege is removed from the list of privileges in the token. The other privileges in the list are reordered to remain contiguous.
SE_PRIVILEGE_USED_FOR_ACCESS 	    = 0x80000000

# Standard access rights | https://msdn.microsoft.com/en-us/library/windows/desktop/aa379607(v=vs.85).aspx
SYNCHRONIZE                         = 0x00100000 #L  # The right to use the object for synchronization. This enables a thread to wait until the object is in the signaled state.


# Token access rights | https://msdn.microsoft.com/en-us/library/windows/desktop/aa374905(v=vs.85).aspx
TOKEN_ADJUST_PRIVILEGES             = 0x00000020   # Required to enable or disable the privileges in an access token
TOKEN_QUERY                         = 0x00000008   # Required to query an access token

# Process access rights for OpenProcess # https://msdn.microsoft.com/en-us/library/windows/desktop/ms684880(v=vs.85).aspx
PROCESS_CREATE_PROCESS              = 0x0080 # Required to create a process.
PROCESS_CREATE_THREAD               = 0x0002 # Required to create a thread.
PROCESS_DUP_HANDLE                  = 0x0040 # Required to duplicate a handle using DuplicateHandle.
PROCESS_QUERY_INFORMATION           = 0x0400 # Required to retrieve certain information about a process, such as its token, exit code, and priority class = see OpenProcessToken #.
PROCESS_QUERY_LIMITED_INFORMATION   = 0x1000 # Required to retrieve certain information about a process = see GetExitCodeProcess, GetPriorityClass, IsProcessInJob, QueryFullProcessImageName #. A handle that has the PROCESS_QUERY_INFORMATION access right is automatically granted PROCESS_QUERY_LIMITED_INFORMATION.  Windows Server 2003 and Windows XP:  This access right is not supported.
PROCESS_SET_INFORMATION             = 0x0200 # Required to set certain information about a process, such as its priority class = see SetPriorityClass #.
PROCESS_SET_QUOTA                   = 0x0100 # Required to set memory limits using SetProcessWorkingSetSize.
PROCESS_SUSPEND_RESUME              = 0x0800 # Required to suspend or resume a process.
PROCESS_TERMINATE                   = 0x0001 # Required to terminate a process using TerminateProcess.
PROCESS_VM_OPERATION                = 0x0008 # Required to perform an operation on the address space of a process = see VirtualProtectEx and WriteProcessMemory #.
PROCESS_VM_READ                     = 0x0010 # Required to read memory in a process using ReadProcessMemory.
PROCESS_VM_WRITE                    = 0x0020 # Required to write to memory in a process using WriteProcessMemory.
PROCESS_ALL_ACCESS                  = (PROCESS_CREATE_PROCESS
                                     | PROCESS_CREATE_THREAD
                                     | PROCESS_DUP_HANDLE
                                     | PROCESS_QUERY_INFORMATION
                                     | PROCESS_QUERY_LIMITED_INFORMATION
                                     | PROCESS_SET_INFORMATION
                                     | PROCESS_SET_QUOTA
                                     | PROCESS_SUSPEND_RESUME
                                     | PROCESS_TERMINATE
                                     | PROCESS_VM_OPERATION
                                     | PROCESS_VM_READ
                                     | PROCESS_VM_WRITE
                                     | SYNCHRONIZE)

# Process creation flags | https://msdn.microsoft.com/en-us/library/windows/desktop/ms684863(v=vs.85).aspx
CREATE_NEW_CONSOLE                  = 0x00000010 # The new process has a new console, instead of inheriting its parent's console (the default).
EXTENDED_STARTUPINFO_PRESENT        = 0x00080000 # The process is created with extended startup information; the lpStartupInfo parameter specifies a STARTUPINFOEX structure.

# UpdateProcThreadAttribute attributes | Specify privileged parent process
ProcThreadAttributeParentProcess    = 0
PROC_THREAD_ATTRIBUTE_INPUT         = 0x00020000                                                          # Attribute is input only
PROC_THREAD_ATTRIBUTE_PARENT_PROCESS= ProcThreadAttributeParentProcess | PROC_THREAD_ATTRIBUTE_INPUT # Handle of the Parent Process

# Win32 API function definitions
                                                                                      # https://msdn.microsoft.com/en-us/library/windows/desktop/ff818516(v=vs.85).aspx

#Retrieves the calling thread's last-error code value. The last-error code is maintained on a per-thread basis. Multiple threads do not overwrite each other's last-error code.
GetLastError = windll.kernel32.GetLastError                                           # https://msdn.microsoft.com/en-us/library/windows/desktop/ms679360(v=vs.85).aspx
GetLastError.restype = DWORD                                                         # DWORD WINAPI GetLastError(void);

# Retrieves a pseudo handle for the current process
GetCurrentProcess = kernel32.GetCurrentProcess                                        # https://msdn.microsoft.com/en-us/library/windows/desktop/ms683179(v=vs.85).aspx
GetCurrentProcess.restype = HANDLE                                                   # HANDLE WINAPI GetCurrentProcess(void);

#  The OpenProcessToken function opens the access token associated with a process
OpenProcessToken = advapi32.OpenProcessToken                                          # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379295(v=vs.85).aspx
OpenProcessToken.restype = BOOL                                                      # BOOL WINAPI OpenProcessToken(
OpenProcessToken.argtypes = [			                                     # (
	         HANDLE,                                                             # HANDLE  ProcessHandle,
	         DWORD,                                                              # DWORD   DesiredAccess,
	         POINTER(HANDLE)	                                             # PHANDLE TokenHandle
	         ]		                                                     # );

PDWORD = POINTER(DWORD)
# The GetTokenInformation function retrieves a specified type of information about an access token
GetTokenInformation = advapi32.GetTokenInformation                                    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa446671(v=vs.85).aspx
GetTokenInformation.restype =  BOOL                                                  # BOOL WINAPI GetTokenInformation
GetTokenInformation.argtypes = [                                                     # (
                 HANDLE,                                                             # HANDLE                  TokenHandle,
                 c_int,                                                              # TOKEN_INFORMATION_CLASS TokenInformationClass, (TOKEN_INFORMATION_CLASS.enum (eg: TokenElevation) -> cast to int (0x14))
                 LPVOID,                                                             # LPVOID                  TokenInformation,
                 DWORD,                                                              # DWORD                   TokenInformationLength,
                 PDWORD                                                              # PDWORD                  ReturnLength
                 ]                                                                   # )

# Opens an existing local process object
OpenProcess = kernel32.OpenProcess                                                    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms684320(v=vs.85).aspx
OpenProcess.restype = HANDLE                                                         # HANDLE WINAPI OpenProcess
OpenProcess.argtypes = [                                                             # (
                 DWORD,                                                              # DWORD dwDesiredAccess,
                 BOOL,                                                               # BOOL  bInheritHandle,
                 DWORD                                                               # DWORD dwProcessId
                 ]                                                                   # )
# Retrieves the process identifier of the calling process
GetCurrentProcessId = kernel32.GetCurrentProcessId                                    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms683180(v=vs.85).aspx
GetCurrentProcessId.restype = DWORD                                                  # DWORD WINAPI GetCurrentProcessId(void);

# Retrieves the base name of the specified module
GetModuleBaseNameA = psapi.GetModuleBaseNameA                                         # https://msdn.microsoft.com/en-us/library/windows/desktop/ms683196(v=vs.85).aspx
GetModuleBaseNameA.restype = DWORD                                                   # DWORD WINAPI GetModuleBaseName
GetModuleBaseNameA.argtypes = [                                                      # (
                 HANDLE,                                                             # HANDLE  hProcess,
                 HMODULE,                                                            # HMODULE hModule,
                 LPTSTR,                                                             # LPTSTR  lpBaseName,
                 DWORD                                                               # DWORD   nSize
                 ]                                                                   # ) 


# The LookupPrivilegeValue function retrieves the locally unique identifier (LUID) used on a specified system to locally represent the specified privilege name
LookupPrivilegeValue = advapi32.LookupPrivilegeValueW                                 # https://msdn.microsoft.com/en-us/library/windows/desktop/aa379180(v=vs.85).aspx Unicode version
LookupPrivilegeValue.restype = BOOL                                                  # BOOL WINAPI LookupPrivilegeValue
LookupPrivilegeValue.argtypes = [                                                    # (
	       	  LPWSTR,                                                            # LPCTSTR lpSystemName,              # LPWSTR ->	 https://msdn.microsoft.com/en-us/library/cc230355.aspx
	       	  LPWSTR,                                                            # LPCTSTR lpName,                    # LPWSTR ->	 https://msdn.microsoft.com/en-us/library/cc230355.aspx
	       	  POINTER(LUID)                                                      # PLUID   lpLuid
	          ]		                                                     # );


PTOKEN_PRIVILEGES = POINTER(TOKEN_PRIVILEGES)
# The AdjustTokenPrivileges function enables or disables privileges in the specified access token
# Enabling or disabling privileges in an access token requires TOKEN_ADJUST_PRIVILEGES access -> PTOKEN_PRIVILEGES = POINTER(TOKEN_PRIVILEGES)
AdjustTokenPrivileges = advapi32.AdjustTokenPrivileges                                # https://msdn.microsoft.com/en-us/library/windows/desktop/aa375202(v=vs.85).aspx
AdjustTokenPrivileges.restype = BOOL                                                 # BOOL WINAPI AdjustTokenPrivileges
AdjustTokenPrivileges.argtypes = [                                                   # {
                  HANDLE,	                                                     #   
		  BOOL,                                                              # BOOL              DisableAllPrivileges,
		  PTOKEN_PRIVILEGES,                                                 # PTOKEN_PRIVILEGES NewState,           # SE_PRIVILEGE_ENABLED = 0x00000002
		  DWORD,	                                                     # DWORD             BufferLength,
		  PTOKEN_PRIVILEGES,                                                 # PTOKEN_PRIVILEGES PreviousState,
	          POINTER(DWORD)                                                     # PDWORD            ReturnLength
	          ]		                                                     # }

# Retrieves the process identifier for each process object in the system.
EnumProcesses = psapi.EnumProcesses                                                   # https://msdn.microsoft.com/en-us/library/windows/desktop/ms682629(v=vs.85).aspx
EnumProcesses.restype = BOOL                                                         # BOOL WINAPI EnumProcesses
EnumProcesses.argtypes = [                                                           # (
                  PDWORD,                                                            # DWORD *pProcessIds,
                  DWORD,                                                             # DWORD cb,
                  PDWORD                                                             # DWORD *pBytesReturned
                  ]                                                                  # )
 
LPTSTR = c_char_p
# Retrieves the name of the executable file for the specified process.
GetProcessImageFileName = psapi.GetProcessImageFileNameA                              # https://msdn.microsoft.com/en-us/library/windows/desktop/ms683217(v=vs.85).aspx
GetProcessImageFileName.restype = DWORD                                              # DWORD WINAPI GetProcessImageFileName
GetProcessImageFileName.argtypes = [                                                 # (
                  HANDLE,                                                            # HANDLE hProcess,
                  LPTSTR,                                                            # LPTSTR lpImageFileName,
                  DWORD                                                              # DWORD  nSize
                  ]                                                                  # )

LPPROC_THREAD_ATTRIBUTE_LIST = LPVOID #PPROC_THREAD_ATTRIBUTE_LIST
PSIZE_T = POINTER(SIZE_T)
# Initializes the specified list of attributes for process and thread creation.
InitializeProcThreadAttributeList = kernel32.InitializeProcThreadAttributeList        # https://msdn.microsoft.com/en-us/library/windows/desktop/ms683481(v=vs.85).aspx
InitializeProcThreadAttributeList.restype = BOOL                                     # BOOL WINAPI InitializeProcThreadAttributeList
InitializeProcThreadAttributeList.argtypes = [                                       # (
                  LPPROC_THREAD_ATTRIBUTE_LIST,                                      # LPPROC_THREAD_ATTRIBUTE_LIST lpAttributeList,
                  DWORD,                                                             # DWORD                        dwAttributeCount,
                  DWORD,                                                             # DWORD                        dwFlags,
                  PSIZE_T                                                            # PSIZE_T                      lpSize
                  ]                                                                  # )

# Updates the specified attribute in a list of attributes for process and thread creation.
UpdateProcThreadAttribute = kernel32.UpdateProcThreadAttribute                        # https://msdn.microsoft.com/en-us/library/windows/deLPSECURITY_ATTRIBUTES lpProcessAttributes,sktop/ms686880(v=vs.85).aspx
UpdateProcThreadAttribute.restype = BOOL                                             # BOOL WINAPI UpdateProcThreadAttribute
UpdateProcThreadAttribute.argtypes = [                                               # (
                  LPPROC_THREAD_ATTRIBUTE_LIST,                                      # LPPROC_THREAD_ATTRIBUTE_LIST lpAttributeList,
                  DWORD,                                                             # DWORD                        dwFlags,
                  DWORD,                                                             # DWORD_PTR                    Attribute,
                  PVOID,                                                             # PVOID                        lpValue,
                  SIZE_T,                                                            # SIZE_T                       cbSize,
                  PVOID,                                                             # PVOID                        lpPreviousValue,
                  PSIZE_T                                                            # PSIZE_T                      lpReturnSize
                  ]                                                                  # )

LPSECURITY_ATTRIBUTES = LPVOID
# Creates a new process and its primary thread. The new process runs in the security context of the calling process.
CreateProcess = kernel32.CreateProcessW                                               # https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx
CreateProcess.restype = BOOL                                                         # BOOL WINAPI CreateProcess
CreateProcess.argtypes = [                                                           # (
                   LPCWSTR,                                                          # LPCTSTR               lpApplicationName,
                   LPWSTR,                                                           # LPTSTR                lpCommandLine,
                   LPSECURITY_ATTRIBUTES,                                            # LPSECURITY_ATTRIBUTES lpProcessAttributes,
                   LPSECURITY_ATTRIBUTES,                                            # LPSECURITY_ATTRIBUTES lpThreadAttributes,
                   BOOL,                                                             # BOOL                  bInheritHandles,
                   DWORD,                                                            # DWORD                 dwCreationFlags,
                   LPVOID,                                                           # LPVOID                lpEnvironment,
                   LPCWSTR,                                                          # LPCTSTR               lpCurrentDirectory,
                   POINTER(STARTUPINFOEX),                                           # LPSTARTUPINFO         lpStartupInfo,
                   POINTER(PROCESS_INFORMATION)                                      # LPPROCESS_INFORMATION lpProcessInformation
                   ]                                                                 # )

# Deletes the specified list of attributes for process and thread creation.
DeleteProcThreadAttributeList = kernel32.DeleteProcThreadAttributeList                # https://msdn.microsoft.com/en-us/library/windows/desktop/ms682559(v=vs.85).aspx
DeleteProcThreadAttributeList.restype = None                                         # VOID WINAPI DeleteProcThreadAttributeList
DeleteProcThreadAttributeList.argtypes = [                                           # (
                   LPPROC_THREAD_ATTRIBUTE_LIST                                      # LPPROC_THREAD_ATTRIBUTE_LIST lpAttributeList
                   ]                                                                 # )

# Closes an open object handle.
CloseHandle = kernel32.CloseHandle                                                    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms724211(v=vs.85).aspx
CloseHandle.restype = BOOL                                                           # BOOL WINAPI CloseHandle
CloseHandle.argtypes =  [                                                            # (
                    HANDLE                                                           # HANDLE hObject
                    ]                                                                # )


# Creates a new process and its primary thread. The new process runs in the security context of the calling process.
CreateProcessAsUser = kernel32.CreateProcessAsUserW                                               # https://msdn.microsoft.com/en-us/library/windows/desktop/ms682425(v=vs.85).aspx
CreateProcessAsUser.restype = BOOL                                                         # BOOL WINAPI CreateProcess
CreateProcessAsUser.argtypes = [                                                           # (
                   HANDLE,                                                           # Handler for user token
                   LPCWSTR,                                                          # LPCTSTR               lpApplicationName,
                   LPWSTR,                                                           # LPTSTR                lpCommandLine,
                   LPSECURITY_ATTRIBUTES,                                            # LPSECURITY_ATTRIBUTES lpProcessAttributes,
                   LPSECURITY_ATTRIBUTES,                                            # LPSECURITY_ATTRIBUTES lpThreadAttributes,
                   BOOL,                                                             # BOOL                  bInheritHandles,
                   DWORD,                                                            # DWORD                 dwCreationFlags,
                   LPVOID,                                                           # LPVOID                lpEnvironment,
                   LPCWSTR,                                                          # LPCTSTR               lpCurrentDirectory,
                   POINTER(STARTUPINFOEX),                                           # LPSTARTUPINFO         lpStartupInfo,
                   POINTER(PROCESS_INFORMATION)                                      # LPPROCESS_INFORMATION lpProcessInformation
                   ]                                                                 # )

userenv.CreateEnvironmentBlock.argtypes = (ctypes.POINTER(ctypes.c_void_p),
                                               ctypes.c_void_p,
                                               ctypes.c_int)
userenv.DestroyEnvironmentBlock.argtypes = (ctypes.c_void_p,)

## END Structs - for use with CTypes


class LockScreen:

    @staticmethod
    def lock_screen(user_name=None):
        ret = False

        # Have rundll run the lock workstation command
        # WinApi.CreateProcessAsUser(
        #   interactiveUserToken,
        #   null,
        #   "rundll32.exe user32.dll,LockWorkStation",
        #   IntPtr.Zero,
        #   IntPtr.Zero,
        #   false,
        #   (uint)WinApi.CreateProcessFlags.CREATE_NEW_CONSOLE |
        #     (uint)WinApi.CreateProcessFlags.INHERIT_CALLER_PRIORITY,
        #   IntPtr.Zero,
        #   currentDirectory,
        #   ref siInteractive,
        #   out piInteractive);

        return ret

    @staticmethod
    def refresh_lock_screen_widget():
        ret = True

        # Kill instances of the lockscreenwidget
        Computer.kill_process(ps_name="lock_screen_widget.exe")
        
        # Copy over files for lockscreenwidget
        cp_command = "xcopy /ECIHRKY /Q %programdata%\\ope\\Services\\lock_screen_widget %programdata%\\ope\\tmp\\lock_screen_widget\\"
        cp_command = os.path.expandvars(cp_command)
        os.system(cp_command)

        # Launch lockscreenwidget
        r = LockScreen.show_lock_screen_widget()
        if not r is True:
            # Lock screen widget started
            p("}}rbError - Unable to start lock_screen_widget!}}xx")
            ret = False

        return ret

    # Try to show a lock screen widget.
    @staticmethod
    def show_lock_screen_widget():
        ret = True

        # If we are not "SYSTEM" user, return true
        if UserAccounts.get_current_user() != "SYSTEM":
            p("show_lock_screen_widget - NOT SYSTEM USER, not launching", log_level=5)
            return True
        
        # Bump up the privileges
        r = UserAccounts.elevate_process_privilege_to_debug()
        r = UserAccounts.elevate_process_privilege_to_tcb()
        r = UserAccounts.elevate_process_privilege_assign_primary_token()
        
        # Find instances of winlogon and launch an app for each instance
        logon_ps_list = {}
        lock_screen_widget_list = {}
        for ps in psutil.process_iter():
            name = str(ps.name())
            pid = str(ps.pid)
            if name.lower() == "winlogon.exe":
                s_id = win32ts.ProcessIdToSessionId(int(pid))
                logon_ps_list[pid] = s_id
            if name.lower() == "lock_screen_widget.exe":
                s_id = win32ts.ProcessIdToSessionId(int(pid))
                lock_screen_widget_list[s_id] = pid
                
        if len(logon_ps_list.keys()) < 1:
            p("No winlogon processes found!")
            return False
        
        #p(str(logon_ps_list))
        #cmd = "c:\\windows\\system32\\notepad.exe"
        #cmd = "C:\\CSE_PORTABLE_CODE\\VSCode\\WPy32-3680\\python-3.6.8\\python.exe C:\\Users\\ray\\Desktop\\git_projects\\ope\\ope\\client_tools\\svc\\lock_screen_widget.py"
        cmd = os.path.expandvars("%programdata%\\ope\\tmp\\lock_screen_widget\\lock_screen_widget.exe")
        if not os.path.exists(cmd):
            p("ERROR - lock_screen_widget.exe (" + cmd + ") is missing!")
            return False

        #p("PIDs: " + str(logon_ps_list))
        for pid in logon_ps_list.keys():
            # The session id of this process
            s_id = logon_ps_list[pid]

            # Is there a lock widget running under this session aready?
            if s_id in lock_screen_widget_list.keys():
                p("lock_screen_widget already running under this session (parent id, widget id, session_id) (" +
                    str(pid) + ", " + str(lock_screen_widget_list[s_id]) + "," + str(s_id) + ")", log_level=5)
                # Skip to the next ps
                continue
            
            try:
                #p("test0 - opening process")
                # Open the process
                ps = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                    0, int(pid)
                    )
            
                # Get the current security token for this process
                #p("test01")
                curr_process_token = win32security.OpenProcessToken(ps, #win32process.GetCurrentProcess(),
                                                    win32security.TOKEN_ALL_ACCESS
                                                    #win32security.TOKEN_DUPLICATE
                                                    )
                
                #p("test02")
                # Copy our process token - so we can modify it
                lock_user_token = win32security.DuplicateTokenEx(curr_process_token,
                                                        win32security.SecurityImpersonation,
                                                        win32security.TOKEN_ALL_ACCESS,
                                                        win32security.TokenPrimary
                                                        #win32security.TokenImpersonation
                                                        )
            except Exception as ex:
                p("Unable to open process - not running as system user? " + str(ex))
                continue

            #p("test03")
            # Adjust privileges
            debug_privilege_id = win32security.LookupPrivilegeValue(
                None,
                win32security.SE_DEBUG_NAME
            )
            assignprimarytoken_privilege_id = win32security.LookupPrivilegeValue(
                None,
                win32security.SE_ASSIGNPRIMARYTOKEN_NAME
            )
            tcb_privilege_id = win32security.LookupPrivilegeValue(
                None,
                win32security.SE_TCB_NAME
            )

            new_privilege = [
                (debug_privilege_id, win32con.SE_PRIVILEGE_ENABLED),
                (assignprimarytoken_privilege_id, win32con.SE_PRIVILEGE_ENABLED),
                (tcb_privilege_id, win32con.SE_PRIVILEGE_ENABLED)
                ]
            #p("test04")
            win32security.AdjustTokenPrivileges(lock_user_token, 
                    0,
                    new_privilege
                    )
            #p("test05")
            # Launch the app with the new privileges
            
            #p("test00")
            Size = SIZE_T(0)
            # Need to get the size first
            r = InitializeProcThreadAttributeList(
                None,
                1,
                0,
                byref(Size)
            )
            #p(r)
            #p(str(Size.value))
            if Size.value == 0:
                p("ERROR - Unable to get size for ProcThreadAttribute List " + str(GetLastError()))
                continue
            #p(int(Size))
            #si.AttributeList = LPPROC_THREAD_ATTRIBUTE_LIST()
            # Allocate memory
            AttributeList = PROC_THREAD_ATTRIBUTE_LIST() #(BYTE * Size.value)()  #PROC_THREAD_ATTRIBUTE_LIST()
            # Make pointer to this process id
            #p("test")
            r = InitializeProcThreadAttributeList(
                byref(AttributeList),
                1,
                0,
                byref(Size)
            )
            #p(r)
            #p("test2")
            # Use ctypes to open this process
            p_handle = OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
            ipid = PVOID(p_handle) #c_long(int(ps.handle))
            #TODO - Parent PID isn't setting properly, why? 
            # using session id right now to determine if an instane is already running for this user.
            #p("Parent PID: " + str(ipid.value) + "/" + str(pid))
            #pv_pid = PVOID(ipid)
            #p("test3")
            r = UpdateProcThreadAttribute(
                byref(AttributeList),
                0, 
                PROC_THREAD_ATTRIBUTE_PARENT_PROCESS,
                byref(ipid),
                sizeof(ipid),
                None,
                None
            )
            #p(r)
            #p("test4")
            # Define our process info
            #si = win32process.STARTUPINFO()
            si = STARTUPINFOEX()
            si.StartupInfo.cb = sizeof(si)
            #p("test06")
            si.StartupInfo.lpDesktop = u"Winsta0\\Winlogon" #LPSTR(b"Winsta0\\Winlogon")
            #p("test07")
            si.AttributeList = addressof(AttributeList)
            
            #p("test08")
            #si.dwFlags = win32process.STARTF_USESHOWWINDOW
            #si.wShowWindow = win32con.SW_NORMAL
            # si.lpDesktop = "WinSta0\Default"  # WinSta0\Winlogon
            #si.lpDesktop = "Winsta0\\Winlogon"

            # Setup envinroment for the user
            #environment = win32profile.CreateEnvironmentBlock(lock_user_token, False)
            WCHAR_SIZE = ctypes.sizeof(ctypes.c_wchar)
            environ = {}
            environment = ctypes.c_void_p()
            userenv.CreateEnvironmentBlock(ctypes.byref(environment), int(lock_user_token), 0)
            addr = environment.value    
            try:
                while True:
                    s = ctypes.c_wchar_p(addr).value
                    if not s:
                        break
                    i = s.find('=', 1)
                    if i != -1:
                        environ[s[:i]] = s[i+1:]
                    addr += (len(s) + 1) * WCHAR_SIZE
            finally:
                pass
                #userenv.DestroyEnvironmentBlock(environment)
            #p(str(environ))
            # Start process as lockscreen user
            #p("test5")
            pi = PROCESS_INFORMATION()
            try:
                # Convert from pyhandle to ctypes handle
                #h_user_token = c_long(int(lock_user_token))
                h_user_token = int(lock_user_token)

                #p("test50")
                # Run as system
                r = CreateProcessAsUser(
                #r = CreateProcess(
                    h_user_token,    # Handle of user token
                    None,               # App Name
                    "\"" + cmd + "\"",  # Command Line (blank if app supplied)
                    None,               # Process Attributes
                    None,               # Thread Attributes
                    0,                  # Inherits Handles
                    ( EXTENDED_STARTUPINFO_PRESENT | CREATE_NEW_CONSOLE ),  # or win32con.CREATE_NEW_CONSOLE,
                    None, #environment,        # Environment
                    os.path.dirname(cmd),  # Curr directory
                    byref(si), # Startup info
                    byref(pi)
                )
                #p(r)
                #p(pi.dwProcessId)
                # (hProcess, hThread, dwProcessId, dwThreadId) = win32process.CreateProcessAsUser(
                #                                 lock_user_token,
                #                                 None,   # AppName (really command line, blank if cmd line supplied)
                #                                 "\"" + cmd + "\"",  # Command Line (blank if app supplied)
                #                                 None,  # Process Attributes
                #                                 None,  # Thread Attributes
                #                                 0,  # Inherits Handles
                #                                 win32con.CREATE_NEW_CONSOLE | win32con.NORMAL_PRIORITY_CLASS | EXTENDED_STARTUPINFO_PRESENT,  # or win32con.CREATE_NEW_CONSOLE,
                #                                 environment,  # Environment
                #                                 os.path.dirname(cmd),  # Curr directory
                #                                 si # Startup info
                #                                 ) 

                # logging.info("Process Started: " + str(dwProcessId))
                # logging.info(hProcess)
                ret = True
            except Exception as e:
                p("Error launching lockscreen process: " + str(e) + "\n" + traceback.format_exc())
                ret = False
            #p("test6")
            # Cleanup used tokens/handles/etc...
            CloseHandle(p_handle)
            userenv.DestroyEnvironmentBlock(environment)
            DeleteProcThreadAttributeList(byref(AttributeList))
            lock_user_token.close()
            curr_process_token.close()
            #p("test7")

            if ret is True:
                p("}}gnPS Run: " + str(cmd) + "}}xx", log_level=3)
            else:
                p("}}rnPS Failed: " + str(cmd) + "}}xx", log_level=3)

        return ret


if __name__ == "__main__":
    LockScreen.show_lock_screen_widget()

    # pi = PROCESS_INFORMATION()
    # p_pi = POINTER(PROCESS_INFORMATION)
    # p = byref(pi)
    # print(p)