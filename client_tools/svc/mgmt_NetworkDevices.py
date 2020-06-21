#import pythoncom
import json
#import win32com.client
import wmi
import os

from color import p
import util

# Need this so scanNics doesn't fail
#pythoncom.CoInitialize()

from mgmt_RegistrySettings import RegistrySettings
from mgmt_Computer import Computer
from mgmt_UserAccounts import UserAccounts


class NetworkDevices:
    # Class to deal with network devices - approved and invalid
    
    # Nics that should always exist (windows makes these and we need them)
    # * - matches any ip
    # -1 - Only matches if NO ip present (adapters that are ok but don't want them "connected")
    # "202.5.222" - partial match - this would match the whole 202.5.222.0/24 network
    # "202." - This would match the whole 202.0.0.0/8 network
    # "202.5.222.5" - Only allow this specific IP (probly not what you want)

    default_microsoft_nics = [
        ("WAN Miniport (IP)", "-1"),
        ("WAN Miniport (IPv6)", "-1"),
        ("WAN Miniport (Network Monitor)", "-1"),
        ("WAN Miniport (PPPOE)", "-1"),
        ("WAN Miniport (PPTP)", "-1"),
        ("WAN Miniport (L2TP)", "-1"),
        ("WAN Miniport (IKEv2)", "-1"),
        ("WAN Miniport (SSTP)", "-1"),
        ("Microsoft Wi-Fi Direct Virtual Adapter", "-1"),
        ("Teredo Tunneling Pseudo-Interface", "-1"),
        ("Microsoft Kernel Debug Network Adapter", "-1"),
        ("Microsoft Virtual WiFi Miniport Adapter", "-1"),
        ("Microsoft Hosted Network Virtual Adapter", "-1"),
    ]

    # Nics that we have approved (e.g. in the sync box)
    default_approved_nics = [
        ("Realtek USB GbE Family Controller", "202.5.222"),  # Sync Box - Del usb adater
        ("Thinkpad USB 3.0 Ethernet Adapter", "202.5.222"),  # Sync Box - Alt IBM adapter
        ("Lenovo USB Ethernet", "202.5.222"),                # Sync Box - Alt IBM adapter
        #("JusticeTechLaptopAdapter", "202.5.222"),  # Justice Tec Laptop NIC
    ]
    default_approved_nics_json = json.dumps(default_approved_nics)

    # List of Nic configurations - grab ALL in one shot to avoid multiple connect/calls later
    _NIC_CONFIGURATION_CACHE = None
    
    # Full list of nics it is ok to use - rebuilt from system, default approved, and registry settings
    NIC_LIST = []

    @staticmethod
    def init_device_list(refresh=False):
        # Build up the nic list
        if not refresh and len(NetworkDevices.NIC_LIST) > 0:
            # Don't rebuild it has been done
            return True
        
        n_list = []
        n_list += NetworkDevices.default_microsoft_nics
        n_list += NetworkDevices.default_approved_nics
        
        # Load the value from the registry
        try:
            approved_nics_json = RegistrySettings.get_reg_value(app="OPEService",
                value_name="approved_nics", default="[]")
            nic_list = json.loads(approved_nics_json)
            for item in nic_list:
                # Add each item to the list
                # p("found nic " + str(item))
                n_list.append(item)

        except Exception as ex:
            p("}}rbUnable to pull approved nics from registry!}}xx")
        
        # Set the current list
        NetworkDevices.NIC_LIST = n_list
        return True
    
    @staticmethod
    def is_nic_approved(nic_name, ip_addresses=[]):
        # Is this nic in the approved list?
        # NOTE - This accounts for the #2, #3 after the nic name
        # Return is (on_list, ip_match)
        # important for nics that are approved but not plugged in
        ret = [False, False]
        
        # Strip off #2, #3, etc...
        for i in range(1,30):
            nic_name = nic_name.replace(" #" + str(i), "")

        # Loop through the list and see if we can find a match
        for nic in NetworkDevices.NIC_LIST:
            name = nic[0]
            subnet = nic[1]
            #if "1000" in nic_name:
            #    print("IS: " + name + " == " + nic_name)
            if name == nic_name:
                # We found the nic, do any of the network subnets match?
                #print(" ----- MATCHED " + name + " against " + nic_name)
                # On list
                ret[0] = True

                if subnet == "-1":
                    # Only approved if NO ip addresses
                    if len(ip_addresses) == 0:
                        ret[1] = True
                        return ret
                    
                elif subnet == "*":
                    # Wildcard match, let it match every IP address
                    ret[1] = True
                    return ret
                else:
                    # Look in the list of IP address for a match
                    for ip in ip_addresses:
                        if subnet in ip:
                            # String is in there (e.g. 202.5.222. is in 202.5.222.34)
                            ret[1] = True
                            return ret

        return ret

    @staticmethod
    def list_approved_nics():
        # Show a list of approved nics
        NetworkDevices.init_device_list()

        # Get the specifically approved nics vs the default approved
        manually_approved_nics = []
        # Load the value from the registry
        try:
            approved_nics_json = RegistrySettings.get_reg_value(app="OPEService",
                value_name="approved_nics", default="[]")
            manually_approved_nics = json.loads(approved_nics_json)
        except Exception as ex:
            p("}}rbUnable to pull approved nics from registry!}}xx")

        p("}}yn+ Pre-approved nics (can't remove)}}xx")
        p("}}mb* Nic manually added to approved list by admin}}xx\n")
        col1 = 45
        col2 = 30
        for item in NetworkDevices.NIC_LIST:
            m = "  "
            if item in manually_approved_nics:
                m = "}}mb* }}xx"
            else:
                m = "}}yn+ }}xx"
            ips = str(item[1])
            if ips == "-1":
                ips = "OK only if no IP (-1)"
            if ips == "*":
                ips = "Any IP Allowed (*)"
            
            p(m + item[0].ljust(col1) + ips.rjust(col2))
    

    @staticmethod
    def approve_nic():
        # Get the params for the nic
        nic_name = util.get_param(2)
        nic_network = util.get_param(3)

        if nic_name == "" or nic_network == "":
            p("}}rbError - Invalid paramaters! try mgmt.exe help approve_nic for more information}}xx")
            return False
        
        nic_id = None
        try:
            nic_id = int(nic_name)
        except:
            # Ok if this fails - trying to see if an ID was passed instead of a name
            pass

        if not nic_id is None:
            # Lookup the nic by ID
            iface = NetworkDevices.get_nic_by_interface_index(nic_id)
            if iface is None:
                # Unable to find an interface by this ID
                p("}}rbInvalid Interface ID! " + str(nic_id) + "}}xx")
                return False
            else:
                #nic_name = iface.Name
                # NOTE - Description will give us the driver name w/out the #2 after it
                nic_name = iface.Description
        
        # Strip off #? at the end of the name
        t_nic = nic_name
        removed_suffix = ""
        for i in range(1,30):
            suffix = " #" + str(i)
            if suffix in t_nic:
                t_nic = t_nic.replace(suffix, "")
                removed_suffix = suffix
        if removed_suffix != "":
            p("}}ybNOTE - Stripped off " + removed_suffix + " from nic name\n - All instances of this nic approved with this network}}xx")
            nic_name = t_nic

        p("}}gnApproving " + nic_name + " on netowrk " + nic_network, log_level=1)

        # Get the list of approved nics
        # Load the value from the registry
        try:
            approved_nics_json = RegistrySettings.get_reg_value(app="OPEService", value_name="approved_nics",
                default="[]")
            nic_list = json.loads(approved_nics_json)
            # Add this nic to the list
            nic_list.append((nic_name, nic_network))
            # Write this back to the registry
            approved_nics_json = json.dumps(nic_list)
            RegistrySettings.set_reg_value(app="OPEService", value_name="approved_nics", value=approved_nics_json)
        except Exception as ex:
            p("}}rbUnable to write approved nics to the registry!}}xx", log_level=1)
            return False

        # Force a reload of the device list
        NetworkDevices.init_device_list(refresh=True)
        
        return True

    @staticmethod
    def remove_nic():
        # Get the params for the nic
        nic_name = util.get_param(2)
        nic_network = util.get_param(3)

        if nic_name == "" or nic_network == "":
            p("}}rbError - Invalid paramaters!}}xx")
            return False
        
        # Get the list of approved nics
        # Load the value from the registry
        try:
            approved_nics_json = RegistrySettings.get_reg_value(app="OPEService", value_name="approved_nics",
                default="[]")
            nic_list = json.loads(approved_nics_json)
            new_nic_list = []
            # Loop through old list and add any that don't match remove parameters
            removed = False
            for item in nic_list:
                #p("checking " + item[0] + " -> " + item[1])
                if item[0] == nic_name and item[1] == nic_network:
                    #p("FOUND!")
                    removed = True
                else:
                    # Not the one to remove, put it in the new_nic_list
                    new_nic_list.append(item)
            
            if removed:
                # Write this back to the registry
                approved_nics_json = json.dumps(new_nic_list)
                RegistrySettings.set_reg_value(app="OPEService", value_name="approved_nics",
                    value=approved_nics_json)
                p("}}gnRemoved " + nic_name + " on netowrk " + nic_network + "}}xx", log_level=1)
            else:
                p("}}rnNOT FOUND - NOT Removed " + nic_name + " on netowrk " + nic_network + " (Can't remove system pre-approved nic entries)}}xx")
        except Exception as ex:
            p("}}rbUnable to write approved nics to the registry!}}xx\n" + str(ex), log_level=1)
            return False
        
        # Force device list refresh
        NetworkDevices.init_device_list(refresh=True)
        
        return True

    @staticmethod
    def get_attributes(obj):
        attribs = dict()
        for p in obj.properties.keys():
            #print(" -- " + str(p) + ": " + str(getattr(obj, p)))
            attribs[p] = getattr(obj, p)
        return attribs

    @staticmethod
    def get_ip_addresses_for_device(interface_index):
        # Build the cache of addresses
        if NetworkDevices._NIC_CONFIGURATION_CACHE is None:
            # Get the list of configurations for ALL nics.
            w = Computer.get_wmi_connection()
            net_configs = w.Win32_NetworkAdapterConfiguration()
            NetworkDevices._NIC_CONFIGURATION_CACHE = dict()
            for c in net_configs:
                i = c.InterfaceIndex
                if not i in NetworkDevices._NIC_CONFIGURATION_CACHE:
                    NetworkDevices._NIC_CONFIGURATION_CACHE[i] = []
                if c.IPAddress is not None:
                    NetworkDevices._NIC_CONFIGURATION_CACHE[i] += c.IPAddress

        ip_addresses = []
        # Find the list of addresses for this adapter if present
        if interface_index in NetworkDevices._NIC_CONFIGURATION_CACHE:
            ip_addresses = NetworkDevices._NIC_CONFIGURATION_CACHE[interface_index]
        
        ret = ip_addresses
            
        return ret

    def get_nic_by_interface_index(interface_index):
        # Find the nic in question
        ret = None

        w = Computer.get_wmi_connection()
        ifaces = w.Win32_NetworkAdapter(InterfaceIndex=interface_index)
        for iface in ifaces:
            ret = iface
        
        return ret


    @staticmethod
    def get_nics_w32():
        # Return a list of nics found in the system
        ret = []

        w = Computer.get_wmi_connection()
        ifaces = w.Win32_NetworkAdapter()
        
        for iface in ifaces:
            attribs = NetworkDevices.get_attributes(iface)

            nic_name = iface.Name
            #dev_id = objItem.NetConnectionID
            nic_network_name = iface.NetConnectionID  # DeviceID?
            nic_if_index = iface.InterfaceIndex
            nic_ip_addresses = NetworkDevices.get_ip_addresses_for_device(nic_if_index)
            #iface.NetworkAddresses  # Default subnet?
            # OK if on
            nic_connected = iface.NetEnabled  # iface.MediaConnnectState # objItem.Status
            nic_enabled = iface.ConfigManagerErrorCode

            ret.append((nic_name, nic_network_name, nic_ip_addresses, nic_connected, nic_enabled, attribs, iface, nic_if_index))
        

        return ret


    @staticmethod
    def get_nics_msft():
        
        # Return a list of nics found in the system
        ret = []

        w = Computer.get_wmi_connection(namespace="StandardCimv2")

        ifaces = w.MSFT_NetAdapter()

        for iface in ifaces:
            
            attribs = NetworkDevices.get_attributes(iface)

            # Note - we may have a #2 or #3 in the name
            nic_name = iface.InterfaceDescription
            #dev_id = objItem.NetConnectionID
            nic_id = iface.Name  # DeviceID?
            nic_network = iface.NetworkAddresses  # Default subnet?
            # (RO) 0-Unknown, 1-Connected, 2-Disconnected
            #nic_connected = iface.MediaConnectState # objItem.Status
            # 1-Up, 2-Down, 3-Testing, 4-Unknown, 5-Dormant, 6-NotPresent, 7-LowerLayerDown
            nic_connected = iface.InterfaceOperationalStatus
            # 1-Up, 2-Down, 3-Testing
            nic_enabled = iface.InterfaceAdminStatus
            
            ret.append((nic_name, nic_id, nic_network, nic_connected, nic_enabled, attribs, iface))
            
            

        return ret

        # Need this so scanNics doesn't fail
        # NOTE - This happens once at the module level
        #pythoncom.CoInitialize()

        # The computer to inspect (localhost)
        strComputer = "."
        # Setup WMI connection
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")

        # Get the list of adapters
        #colItems = objSWbemServices.ExecQuery("Select * from Win32_NetworkAdapter")
        #colItems = objSWbemServices.ExecQuery("Select * from MSFT_NetAdapter")
        colItems = objSWbemServices.ExecQuery("Select * from Win32_NetworkAdapterConfiguration")
        

        for objItem in colItems:
            # DEBUG - Dump attributes
            attribs = NetworkDevices.dump_attributes(objItem)
            
            # Note - we may have a #2 or #3 in the name
            nic_name = objItem.Name
            #dev_id = objItem.NetConnectionID
            nic_id = objItem.DeviceName  # DeviceID?
            nic_network = ""  # Default subnet?
            # (RO) 0-Unknown, 1-Connected, 2-Disconnected
            nic_connected = objItem.MediaConnnectState # objItem.Status
            nic_enabled = False

            #net_enabled = objItem.NetEnabled
            # True if this is a physical adapter
            #connector_present = objItem.ConnectorPresent
            # (RO) Is this a hidden device - such as kernel debug driver?
            #device_hidden = objItem.Hidden
            # (RO) 1-Up, 2-Down, 3-Testing - Admin status?
            #admin_status = objItem.InterfaceAdminStatus
            # Unique name assigned during installatin?
            #interface_description = objItem.InterfaceDescription
            # Current operation status 1-Up, 2-Down, 3-Testing, 4-Unknown, 5-Dormant, 6-NotPresent, 7-LowerLayerDown
            #interface_operation_status = objItem.InterfaceOperationStatus
            # What kind of adapter is it?
            # 0-Unknown, 1-Other, 2-Ethernet, 3-IB, 4-FC, 5-FDDI, 6-ATM, 7-TokenRing, 8-FrameRelay, 9-Infrared
            # 10-BlueTooth, 11-WirelessLan, 
            #link_technology = objItem.LinkTechnology

            # Media connected state (plugged in?)
            # 0-Unknown, 1-Connected, 2-Disconnected
            #media_connect_state = objeItem.MediaConnnectState

            # Can this adapter be removed by the user?
            #not_user_removable = objItem.NotUserRemovable



            nic_addresses = objItem.NetworkAddresses
            if nic_addresses:
                for a in nic_addresses:
                    # print("Network Address " + str(a))
                    ip_network += a

            ret.append((nic_name, nic_id, nic_network, nic_connected, nic_enabled, attribs, iface))

        # Cleanup
        #pythoncom.CoUninitialize()

        return ret

    @staticmethod
    def filter_local_link_ip_addresses(ip_addresses):
        ret = []

        # Remove APIPA IP Addresses (Local Link Addresses)
        # These are the auto 169.254.?.? addresses you get if you don't get a
        # valid DHCP response (or briefly while waiting for one)
        # IP6 is fe80::/10
        for ip in ip_addresses:
            # Filter out local link addresses
            if not "169.254." in ip and not "fe80::" in ip:
                ret.append(ip)
        
        return ret

    @staticmethod
    def list_system_nics():
        NetworkDevices.init_device_list()
        verbose = util.get_param(2, "").strip("-")
        if verbose == "verbose":
            verbose = "v"

        # Get a list of nics currently in the system
        nics_found = NetworkDevices.get_nics_w32()
        for nic in nics_found:
            (nic_name, nic_network_name, nic_ip_addresses, nic_connected, nic_enabled, attribs, iface, nic_if_index) = nic
            filtered_nic_ip_addresses = NetworkDevices.filter_local_link_ip_addresses(nic_ip_addresses)

            if nic_network_name != "None" and nic_network_name is not None:
                nic_network_name = "}}wn(}}cn" + "{0:>10}".format(nic_network_name) + "}}wn)"
            else:
                nic_network_name = "" # "}}wn(" + "{0:>10}".format("None") + ")"

            if nic_ip_addresses is None:
                nic_ip_addresses = []
            
            if nic_connected is True:
                nic_connected = "}}yb" + "Connected".ljust(12) + "}}xx"
            else:
                nic_connected = "}}yn" + "Disconnected".ljust(12) + "}}xx"

            # 1-Up, 2-Down, 3-Testing
            if nic_enabled == 0:
                nic_enabled = "}}yb" + "Enabled".rjust(9) + "}}xx"
            elif nic_enabled == 22:
                nic_enabled = "}}yn" + "Disabled".rjust(9) + "}}xx"
            else:
                nic_enabled = "}}rn" + "Unplugged".rjust(9) + "}}xx"

            # Use nic description to check approved status - no #2 etc... at the end
            nic_description = iface.Description
            
            # Not approved - show as X
            approved_status = "}}rbX}}xx"
            # Returns T/F for (matched_name, matched_ip)
            r = NetworkDevices.is_nic_approved(nic_description, filtered_nic_ip_addresses)
            num_ips = len(filtered_nic_ip_addresses)
            if r[0] is True and r[1] is True:
                # Approved and good IP - show as good
                approved_status = "}}gb+}}xx"
            elif r[0] is True and r[1] is False and num_ips == 0:
                # Approved but no IP
                approved_status = "}}yb?}}xx"
            elif r[0] is True and r[1] is False and num_ips > 0:
                approved_status = "}}rb!}}xx"
            
            ip_address_str = ""
            if len(nic_ip_addresses) > 0:
                ip_address_str = "\n\t}}cn" + str(nic_ip_addresses) + "}}xx"


            p(approved_status + \
                 "}}gn" + " {0:>2}".format(nic_if_index) + \
                " }}wn" + "{0:43}".format(nic_name) + \
                " " + nic_enabled + \
                "/" + nic_connected + \
                
                " " + nic_network_name + \
                " " + ip_address_str + \
                "}}xx")
            if verbose == "v":
                p("}}cn-- " + str(attribs) + "}}xx")

        p("\n}}gb+ }}xxApproved/Connecte, }}yb? }}xxApproved/Not Connected, }}rbX }}xxNot Approved}}xx, }}rb! }}xxApproved/Invalid IP}}xx")
        p("}}rbNOTE}}xx - Approved Nics w/out IPs (or with 169.254/fe80::) will be enabled so they can use DHCP}}xx")

        return True

    @staticmethod
    def disable_nic(interface_index):
        #w = wmi.WMI(namespace="StandardCimv2")
        w = Computer.get_wmi_connection(namespace="StandardCimv2")

        ifaces = w.MSFT_NetAdapter(InterfaceIndex=interface_index)
        for iface in ifaces:
            out = ""
            iface.Disable(out)
            if out !="":
                p("OUTPUT: " + str(out))
            #iface.Lock()

        return True

    @staticmethod
    def enable_nic(interface_index):
        #w = wmi.WMI(namespace="StandardCimv2")
        w = Computer.get_wmi_connection(namespace="StandardCimv2")

        ifaces = w.MSFT_NetAdapter(InterfaceIndex=interface_index)
        for iface in ifaces:
            out = ""
            iface.Enable(out)
            if out !="":
                p("OUTPUT: " + str(out))
            #Admin lock
            #iface.Lock()
            
        return True

    @staticmethod
    def disable_wlan_hosted_network():
        # TODO - Not turning off w/out the network inteface being off??
        # Disable the hostednetwork option for wlan devices in windows
        cmd = "netsh wlan stop hostednetwork"
        os.system(cmd)
        cmd = "netsh wlan set hostednetwork mode=disallow"
        os.system(cmd)
        # netsh wlan show settings - to view settings
    
    @staticmethod
    def enable_wlan_hosted_network():
        # Enable the hostednetwork option for wlan devices in windows
        cmd = "netsh wlan set hostednetwork mode=allow"
        os.system(cmd)
        cmd = "netsh wlan start hostednetwork"
        os.system(cmd)
        

    @staticmethod
    def scan_nics():
        # May need to call this before calling this function so that COM works
        # pythoncom.CoInitialize() - called in the main function
        
        # Make sure device list is initialized
        NetworkDevices.init_device_list()

        p("scanning for unauthorized nics...", log_level=4)

        nic_list = NetworkDevices.get_nics_w32()

        for nic in nic_list:
            (nic_name, nic_network_name, nic_ip_addresses, nic_connected, nic_enabled, attribs, iface, nic_if_index) = nic
            # Make sure we remove local link ips (169.254.?.?)
            filtered_nic_ip_addresses = NetworkDevices.filter_local_link_ip_addresses(nic_ip_addresses)

            # NOTE - nic_enabled - 0 = enabled, 22 = disabled, all others - ?? (not enabled)
            # Use nic descrition to match - it doesn't have #2 etc.. at the end
            nic_description = iface.Description
            # Returns T/F for (matched_nic_name, matched_nic_ip)
            r = NetworkDevices.is_nic_approved(nic_description, filtered_nic_ip_addresses)
            num_ips = len(filtered_nic_ip_addresses)

            # Possible on scenarios, 
            # A - Nic is not approved (IP doesn't matter) - turn off
            # B - Nic is on, approved, and has good IP - leave alone
            # C - Nic is on, approved, has NO IP (e.g. unplugged/offline) - allow DHCP attempts
            # D - Nic is on, approved, has BAD IP! (good adapter plugged into bad network!)
            #       *** NOTE - This is security issue - who plugged into bad network!?!
            
            # Possible off scenarios
            # E - Nic is off, not approved, IP doesn't matter
            # F - Nic is off, approved, has no IP - needs to turn on and allow DHCP
            # 

            # A - If adapter isn't on the list, kill it. 
            if r[0] is not True and nic_enabled == 0:
                p("}}ynUnApproved NIC Detected (NO IP) - Disabling " + \
                    nic_name + "}}xx", log_level=1)
                try:
                    NetworkDevices.disable_nic(nic_if_index)
                except Exception as ex:
                    p("}}rb** ERROR - UNABLE TO DISABLE DEVICE: " + nic_name + "}}xx\n" + 
                        str(ex), log_level=1)
                continue
            
            # B - Nic is approved and has good IP and is on
            if r[0] is True and r[1] is True and nic_enabled == 0:
                # Good nic, good ip, adapter on.
                p("}}gn** Nic approved and good ip: " + nic_name + "}}xx", log_level=5)
                continue

            # C - Nic is on, approved, has no IP (should be trying to get IP via DHCP)
            if r[0] is True and num_ips == 0 and nic_enabled == 0:
                # Good nic, waiting for dhcp, adapter on.
                p("}}gn** Nic approved, waiting for dhcp: " + nic_name + "}}xx",
                    log_level=5)
                continue

            # D - Nic is on, approved, has BAD IP! (good adapter plugged into bad network!)
            #       *** NOTE - This is security issue - who plugged into bad network!?!
            if r[0] is True and nic_enabled == 0 and r[1] is False and num_ips > 0:
                # Good nic on bad network. disable it!
                curr_user = UserAccounts.get_active_user_name()
                p("}}rb** Approved NIC on BAD IP Network Detected - Disabling " + \
                    nic_name + " " + str(nic_ip_addresses) + " - why is this plugged into another network?!}}xx",
                    log_level=1)
                try:
                    NetworkDevices.disable_nic(nic_if_index)
                except Exception as ex:
                    p("}}rb** ERROR - UNABLE TO DISABLE DEVICE: " + nic_name + "}}xx\n" + 
                        str(ex), log_level=1)
                continue

            # E - Nic is off, not approved, IP doesn't matter
            if nic_enabled == 22 and r[0] is not True:
                # Bad nic - already off
                p("}}yn** Unapproved nic, already disabled " + nic_name + "}}xx",
                    log_level=4)
                continue
                
            # F - Nic is off, approved, has no IP - needs to turn on and allow DHCP
            if nic_enabled == 22 and r[0] is True:
                # Turn on so it can try for DHCP address
                p("}}gb** Approved nic found disabled, enabling " + nic_name + "}}xx",
                    log_level=4)
                try:
                    NetworkDevices.enable_nic(nic_if_index)
                except Exception as ex:
                    p("}}rb** ERROR - UNABLE TO ENABLE DEVICE: " + nic_name + "}}xx\n" + 
                        str(ex), log_level=1)
                continue

            # If none of the previous entries match, kill the device if it is enabled
            if nic_enabled == 0:
                # Failsafe
                p("}}rb**** No rule for this nic, disabling! " + nic_name + "}}xx")
                try:
                    NetworkDevices.disable_nic(nic_if_index)
                except Exception as ex:
                    p("}}rb** ERROR - UNABLE TO DISABLE DEVICE: " + nic_name + "}}xx\n" + 
                        str(ex), log_level=1)
                continue

            # OLD commands
            #cmd = "netsh interface set interface \"" + dev_id + "\" admin=ENABLED"
            #cmd = "netsh interface set interface \"" + dev_id + "\" admin=DISABLED"
    
        return True
    
    @staticmethod
    def device_event():
        # A device event happened (device plugged in?)

        # TODO - detect types of device events?
        # for now, just run scan nics which will kick off any bad devices
        p("}}ynDevice Event Detected! Scanning nics...}}xx")
        return NetworkDevices.scan_nics()