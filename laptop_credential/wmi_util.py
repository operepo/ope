

import wmi


def show_wmi_classes(w):

    # See list of classes 
    for class_name in w.classes:
        if 'User' in class_name or 'Account' in class_name:
            print("Class: " + str(class_name))
        
        

def show_wmi_methods(item):
    print(item)
    for k in item.methods.keys():
        print("Method: " + str(k))

def show_wmi_properties(item):
    for p in item.properties.keys():
        print("Prop: " + p + " -> " + str(getattr(item, p)))


def show_wmi_processes(w, process_name):
    for p in w.Win32_Process(name=process_name):
        print("LMS Process: " + str(p.Caption))
    
def kill_wmi_process(w, process_name):
    for p in w.Win32_Process(name=process_name):
        print("Killing Process: " + str(p.Name))
        p.Terminate()
        
def show_wmi_net_interfaces(w):
    for i in w.Win32_NetworkAdapterConfiguration(IPEnabled=1):
        print("Int: " + str(i.Description) + "  " + str(i.MACAddress))
        for ip in i.IPAddress:
            print("IP Addr: " + str(ip))
        
def show_wmi_removable_drives(w):
    DRIVE_TYPES = {
        0: "Unknown",
        1: "No Root Directory",
        2: "Removable Disk",
        3: "Local Disk",
        4: "Network Drive",
        5: "Compact Disk",
        6: "RAM Disk"
    }
    
    for drive in w.Win32_LogicalDisk():
        # if drive.DriveType != 3:
        # NOTE - Picking up some USB drives as local?
        print("Found Drive: " + drive.Caption + " (" + DRIVE_TYPES[drive.DriveType] + ")")
        print(drive)
            

w = wmi.WMI()


# show_wmi_classes(w)


# Win32_LoggedOnUser
# Win32_AccountSID
# Win32_Account
# Win32_UserProfile
# Win32_UserDesktop
# Win32_UserAccount
item = w.Win32_Account

show_wmi_methods(item)
show_wmi_properties(item)


#show_wmi_processes(w, "OPE_LMS.exe")
#kill_wmi_process(w, "OPE_LMS.exe")

#show_wmi_net_interfaces(w)
#show_wmi_removable_drives(w)
        
