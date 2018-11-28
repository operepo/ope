import sys
import os
import win32api
import win32con
import win32netcon
import ntsecuritycon
import win32security
import win32net
import ctypes
import enum
try:
    import _winreg as winreg
except:
    import winreg

    
import winsys
from winsys import accounts, registry, security

from term import p

STUDENTS_GROUP = "OPEStudents"


#import gluon.contrib.aes as AES
import pyaes as AES
import threading
import base64


def fast_urandom16(urandom=[], locker=threading.RLock()):
    """
    this is 4x faster than calling os.urandom(16) and prevents
    the "too many files open" issue with concurrent access to os.urandom()
    """
    try:
        return urandom.pop()
    except IndexError:
        try:
            locker.acquire()
            ur = os.urandom(16 * 1024)
            urandom += [ur[i:i + 16] for i in xrange(16, 1024 * 16, 16)]
            return ur[0:16]
        finally:
            locker.release()


def pad(s, n=32, padchar=' '):
    if len(s) == 0:
        # Handle empty value - pad it out w empty data
        s += padchar * n
        return s
    while ((len(s) % n) != 0):
        s += padchar
    #pad_len = len(s) % 32 # How many characters do we need to pad out to a multiple of 32
    #if (pad_len != 0):
    #    #return s + (32 - len(s) % 32) * padchar
    #    return s + (
    return s


def AES_new(key, iv=None):
    """ Returns an AES cipher object and random IV if None specified """
    if iv is None:
        iv = fast_urandom16()

    # return AES.new(key, AES.MODE_CBC, IV), IV
    # Util.aes = pyaes.AESModeOfOperationCBC(key, iv = iv)
    # plaintext = "TextMustBe16Byte"
    # ciphertext = aes.encrypt(plaintext)
    return AES.AESModeOfOperationOFB(key, iv = iv), iv


def encrypt(data, key):
    key = pad(key[:32])
    cipher, iv = AES_new(key)
    encrypted_data = iv + cipher.encrypt(pad(data, 16))
    return base64.urlsafe_b64encode(encrypted_data)


def decrypt(data, key):
    key = pad(key[:32])
    if data is None:
        data = ""
    try:
        data = base64.urlsafe_b64decode(data)
    except TypeError as ex:
        # Don't let error blow things up
        pass
    iv, data = data[:16], data[16:]
    try:
        cipher, _ = AES_new(key, iv=iv)
    except:
        # bad IV = bad data
        return data
    try:
        data = cipher.decrypt(data)
    except:
        # Don't let error blow things up
        pass
    data = data.rstrip(' ')
    return data

def test_reg():
    global STUDENTS_GROUP
    
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software", 0,
        winreg.KEY_WOW64_64KEY | winreg.KEY_READ)
    
    p("SUB KEYS: ")
    enum_done = False
    i = 0
    try:
        while enum_done is False:
            sub_key = winreg.EnumKey(key, i)
            p("-- SK: " + str(sub_key))
            i += 1
            # p("Ref: " + str(winreg.QueryReflectionKey(winreg.HKEY_LOCAL_MACHINE)))
    except WindowsError as ex:
        # No more values
        if ex.errno == 22:
            # p("---_DONE")
            # Don't flag an error when we are out of entries
            pass
        else:
            p("-- ERR " + str(ex) + " " + str(ex.errno))
        pass


def get_credentialed_student_name(default_value=""):
    
    ret = default_value
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software\\OPE\\OPELMS\\student", 0,
            winreg.KEY_WOW64_64KEY | winreg.KEY_READ)
        val = winreg.QueryValueEx(key, 'user_name')
        ret = val
    except Exception as ex:
        # p("err: " + str(ex))
        pass
        
    return ret
    
    
def set_registry_value(key, value):
    
    key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, "Software\\OPE\\OPELMS\\student",
        0, winreg.KEY_WOW64_64KEY | winreg.KEY_WRITE)
    
    winreg.SetValueEx(key, key, 0, winreg.REG_SZ, value)
    
    
    
    # try:
        
        # key = win_util.get_reg_key(r"HKEY_LOCAL_MACHINE\Software\OPE\OPELMS\student")
        # last_student_user = key.get_value("user_name")        
    # except winsys.exc.x_not_found as error_message:
    #    p("}}rbKey Not Found}}xx" + str(error_message))
    #    ok if it isn't here, just wasn't credentialed previously
        # pass
    # except Exception as error_message:
        # p("}}rbERR }}xx" + str(error_message))
        # return False
        # pass
    
def create_local_student_account(user_name, full_name, password):
    global STUDENTS_GROUP

    # Ensure the Students group exists
    ret = create_local_students_group()

    # Create local student account
    student = None
    try:
        p("}}yn\tAdding student account...}}xx")
        accounts.User.create(user_name, password)
    except pywintypes.error as err:
        if err[2] == "The account already exists.":
            pass
        else:
            # Unexpected error
            p("}}rb" + str(err) + "}}xx")
            ret = False

    # Get the student object
    student = accounts.user(user_name)
    # Set properties for this student
    # win32net.NetUserChangePassword(None, user_name, old_pw, password)

    user_data = dict()
    user_data['name'] = user_name
    user_data['full_name'] = full_name
    user_data['password'] = password
    user_data['flags'] = win32netcon.UF_NORMAL_ACCOUNT | win32netcon.UF_PASSWD_CANT_CHANGE | win32netcon.UF_DONT_EXPIRE_PASSWD | win32netcon.UF_SCRIPT
    user_data['priv'] = win32netcon.USER_PRIV_USER
    user_data['comment'] = 'OPE Student Account'
    # user_data['home_dir'] = home_dir
    # user_data['home_dir_drive'] = "h:"
    user_data['primary_group_id'] = ntsecuritycon.DOMAIN_GROUP_RID_USERS
    user_data['password_expired'] = 0
    user_data['acct_expires'] = win32netcon.TIMEQ_FOREVER
    
    win32net.NetUserSetInfo(None, user_name, 3, user_data)

    # Add student to the students group
    p("}}yn\tAdding student to students group...}}xx")
    grp = accounts.LocalGroup(accounts.group(STUDENTS_GROUP).sid)
    users_grp = accounts.LocalGroup(accounts.group("Users").sid)
    try:
        # Add to students group
        grp.add(student)
    except pywintypes.error as err:
        if err[2] == "The specified account name is already a member of the group.":
            pass
        else:
            # Unexpected error
            p("}}rb" + str(err) + "}}xx")
            ret = False
    try:
        # Add to users group
        users_grp.add(student)
    except pywintypes.error as err:
        if err[2] == "The specified account name is already a member of the group.":
            pass
        else:
            # Unexpected error
            p("}}rb" + str(err) + "}}xx")
            ret = False

    # # home_dir = "%s\\%s" % (server_name, user_name)
    #

    return ret


def create_local_students_group():
    global STUDENTS_GROUP
    # Ensure the local students group exists
    ret = True
    try:
        accounts.LocalGroup.create(STUDENTS_GROUP)
    except pywintypes.error as err:
        if err[2] == "The specified local group already exists.":
            pass
        else:
            # Unexpected error
            p("}}rb" + str(err) + "}}xx")
            ret = False

    return ret

    
def disable_student_accounts():
    # Get a list of accounts that are in the students group
    global STUDENTS_GROUP

    try:
        grp = accounts.local_group(STUDENTS_GROUP)
    except winsys.exc.x_not_found as ex:
        # p("}}yn" + str(STUDENTS_GROUP) + " group not found - skipping disable student accounts...}}xx")
        return
    
    for user in grp:
        user_name = str(user)
        p("}}cnDisabling Student Account: " + user_name + " in " + STUDENTS_GROUP + "...}}xx")
        
        user_data = dict()
        user_data['flags'] = win32netcon.UF_SCRIPT | win32netcon.UF_ACCOUNTDISABLE
        win32net.NetUserSetInfo(".", user.name, 1008, user_data)
    
def delete_user(user_name):
    # Remove the local user
    accounts.User(user_name).delete()


def disable_guest_account():
    pass
    # Run this to disable the guest account?
    # NET USER Guest /ACTIVE:no


def create_reg_key(key_str, user_name=None):
    reg = registry.create(key_str)

    # Add the user to the key with permissions
    with reg.security() as s:
        # Break inheritance causes things to reapply properly
        s.break_inheritance(copy_first=True)
        if user_name is not None:
            s.dacl.append((user_name, "R", "ALLOW"))
        s.dacl.append((accounts.me(), "F", "ALLOW"))
        # s.dacl.dump()
    return reg

def get_reg_key(key_str, user_name=None):
    reg = registry.registry(key_str)
    
    with reg.security() as s:
        # Break inheritance causes things to reapply properly
        s.break_inheritance(copy_first=True)
        if user_name is not None:
            s.dacl.append((user_name, "Q", "ALLOW"))
        s.dacl.append((accounts.me(), "F", "ALLOW"))
        # s.dacl.dump()
    return reg

# def reorder_acls(acl_list):
#     # Order acls in this order
#     # 1 - Access denied on object
#     # 2 - Access denied on child or property
#     # 3 - Access allowed on object
#     # 4 - Access allowed on child or property
#     # 5 - All inherited ACEs
#
#     deny_object = list()
#     deny_other = list()
#     allow_object = list()
#     allow_other = list()
#     inherited = list()
#
#     for i in range(acl_list.GetAceCount()):
#         ace = acl_list.GetAce(i)
#         if ace[0][1] & win32security.INHERITED_ACE:
#             inherited.append(ace)
#         elif ace[0][0] == win32security.ACCESS_ALLOWED_ACE_TYPE:
#             allow_other.append(ace)
#         elif ace[0][0] == win32security.ACCESS_ALLOWED_OBJECT_ACE_TYPE:
#             allow_object.append(ace)
#         elif ace[0][0] == win32security.ACCESS_DENIED_ACE_TYPE:
#             deny_other.append(ace)
#         elif ace[0][0] == win32security.ACCESS_DENIED_OBJECT_ACE_TYPE:
#             deny_object.append(ace)
#
#         print("ACE: " + str(win32security.LookupAccountSid(None, ace[2])) + " - " + str(ace))
#
#     print("deny object " + str(deny_object))
#     print("deny other " + str(deny_other))
#     print("allow object " + str(allow_object))
#     print("allow other " + str(allow_other))
#     print("inherited " + str(inherited))
#
#     # Reassemble aces into a list
#     ret = win32security.ACL()
#
#     # deny
#     for d in deny_other:
#         ret.AddAccessDeniedAceEx(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2]
#                                )
#     # deny object
#     for d in deny_object:
#         ret.AddAccessDeniedObjectAce(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2], d[3], d[4]
#                                )
#     # allow
#     for d in allow_other:
#         ret.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2]
#                                )
#     # allow object
#     for d in allow_object:
#         ret.AddAccessAllowedObjectAce(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2], d[3], d[4]
#                                )
#     # inherited
#     print("Inherited: ")
#     for d in inherited:
#         if d[0][0] == win32security.ACCESS_ALLOWED_ACE_TYPE:
#             ret.AddAccessAllowedAceEx(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2]
#                                )
#             print("ALLOWED " + str(win32security.LookupAccountSid(None, d[2])))
#         elif d[0][0] == win32security.ACCESS_ALLOWED_OBJECT_ACE_TYPE:
#             ret.AddAccessAllowedObjectAce(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2], d[3], d[4]
#                                )
#             print("ALLOWED OBJ " + str(win32security.LookupAccountSid(None, d[2])))
#         elif d[0][0] == win32security.ACCESS_DENIED_ACE_TYPE:
#             ret.AddAccessDeniedAceEx(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2]
#                                )
#             print("DENIED " + str(win32security.LookupAccountSid(None, d[2])))
#         elif d[0][0] == win32security.ACCESS_DENIED_OBJECT_ACE_TYPE:
#             ret.AddAccessDeniedObjectAce(win32security.ACL_REVISION_DS,
#                                d[0][1], d[1], d[2], d[3], d[4]
#                                )
#             print("DENIED OBJ " + str(win32security.LookupAccountSid(None, d[2])))
#     return ret
#
#
# def add_user_to_key(reg_key, user_name=""):
#
#     return True


# def create_user_security_descriptor(user_name):
#     sid_user = win32security.LookupAccountName(user_name)
#     sd = win32security.SECURITY_DESCRIPTOR()
#
#     # Create well known SID for the administrators group
#     sub_auths = ntsecuritycon.SECURITY_BUILTIN_DOMAIN_RID, \
#         ntsecuritycon.DOMAIN_ALIAS_RID_ADMINS
#     sid_admins = win32security.SID(ntsecuritycon.SECURITY_NT_AUTHORITY, sub_auths)
#
#     # Create ACL with user and admins full access
#     acl = win32security.ACL(128)
#     acl.AddAccessAllowedAce(win32file.FILE_ALL_ACCESS, sid_user)
#     acl.AddAccessAllowedAce(win32file.FILE_ALL_ACCESS, sid_admins)
#
#     sd.SetSecurityDescriptorDacl(1, acl, 0)
#
#     return sd
