#import pythoncom
import json
#import win32com.client
import wmi

from color import p
import util

# Need this so scanNics doesn't fail
#pythoncom.CoInitialize()

from mgmt_RegistrySettings import RegistrySettings

from mgmt_EventLog import EventLog

global LOGGER
LOGGER = EventLog.get_current_instance()


class NetworkDevices:
    # Class to deal with network devices - approved and invalid
    
    # Nics that should always exist (windows makes these and we need them)
    default_microsoft_nics = [
        ("WAN Miniport (IP)", "*"),
        ("WAN Miniport (IPv6)", "*"),
        ("WAN Miniport (Network Monitor)", "*"),
        ("WAN Miniport (PPPOE)", "*"),
        ("WAN Miniport (PPTP)", "*"),
        ("WAN Miniport (L2TP)", "*"),
        ("WAN Miniport (IKEv2)", "*"),
        ("WAN Miniport (SSTP)", "*"),
        ("Microsoft Wi-Fi Direct Virtual Adapter", "*"),
        ("Teredo Tunneling Pseudo-Interface", "*"),
        ("Microsoft Kernel Debug Network Adapter", "*"),
    ]

    # Nics that we have approved (e.g. in the sync box)
    default_approved_nics = [
        ("Realtek USB GbE Family Controller", "202.5.222"),  # Sync Box - Del usb adater
        ("Thinkpad USB 3.0 Ethernet Adapter", "202.5.222"),  # Sync Box - Alt IBM adapter
        #("JusticeTechLaptopAdapter", "202.5.222"),  # Justice Tec Laptop NIC
    ]
    default_approved_nics_json = json.dumps(default_approved_nics)

    # List of Nic configurations - grab ALL in one shot to avoid multiple connect/calls later
    _NIC_CONFIGURATION_CACHE = None
    
    # More nics we can use when debugging (in python mode, not binary)
    # debug_nics = [ "Intel(R) 82579LM Gigabit Network Connection",
    #                "150Mbps Wireless 802.11bgn Nano USB Adapter",
    #                "Intel(R) PRO/1000 MT Network Connection",
    #                "Intel(R) Centrino(R) Wireless-N 1000"
    #              ]

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
        
        # Load the value from the registry
        try:
            approved_nics_json = RegistrySettings.get_reg_value(app="OPEService", value_name="approved_nics",
                default=NetworkDevices.default_approved_nics_json)
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
        is_approved = False

        # Strip off #2, #3, etc...
        for i in range(1,20):
            nic_name = nic_name.replace(" #" + str(i), "")

        # Loop through the list and see if we can find a match
        for nic in NetworkDevices.NIC_LIST:
            name = nic[0]
            subnet = nic[1]

            if name == nic_name:
                # We found the nic, do any of the network subnets match?
                if subnet == "*":
                    # Wildcard match, let it match every IP address
                    is_approved = True
                    return is_approved
                # Look in the list of IP address for a match
                for ip in ip_addresses:
                    if subnet in ip:
                        # String is in there (e.g. 202.5.222. is in 202.5.222.34)
                        is_approved = True
                        return is_approved

        return is_approved

    @staticmethod
    def list_approved_nics():
        # Show a list of approved nics
        NetworkDevices.init_device_list()

        for item in NetworkDevices.NIC_LIST:
            p(item[0] + " -> " + str(item[1]))
    

    @staticmethod
    def approve_nic():
        global LOGGER
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
                nic_name = iface.Name
        
        # Strip off #? at the end of the name
        t_nic = nic_name
        removed_suffix = ""
        for i in range(1,20):
            suffix = " #" + str(i)
            if suffix in t_nic:
                t_nic = t_nic.replace(suffix, "")
                removed_suffix = suffix
        if removed_suffix != "":
            p("}}ybNOTE - Stripped off " + removed_suffix + " from nic name\n - All instances of this nic approved with this network}}xx")
            nic_name = t_nic

        LOGGER.log_event("}}gnApproving " + nic_name + " on netowrk " + nic_network, log_level=1)

        # Get the list of approved nics
        # Load the value from the registry
        try:
            approved_nics_json = RegistrySettings.get_reg_value(app="OPEService", value_name="approved_nics",
                default=NetworkDevices.default_approved_nics_json)
            nic_list = json.loads(approved_nics_json)
            # Add this nic to the list
            nic_list.append((nic_name, nic_network))
            # Write this back to the registry
            approved_nics_json = json.dumps(nic_list)
            RegistrySettings.set_reg_value(app="OPEService", value_name="approved_nics", value=approved_nics_json)
        except Exception as ex:
            LOGGER.log_event("}}rbUnable to write approved nics to the registry!}}xx", log_level=1)
            return False
        
        return True

    @staticmethod
    def remove_nic():
        global LOGGER
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
                default=NetworkDevices.default_approved_nics_json)
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
                RegistrySettings.set_reg_value(app="OPEService", value_name="approved_nics", value=approved_nics_json)
                LOGGER.log_event("}}gnRemoved " + nic_name + " on netowrk " + nic_network + "}}xx", log_level=1)
            else:
                p("}}rnNOT FOUND - NOT Removed " + nic_name + " on netowrk " + nic_network + "}}xx")
        except Exception as ex:
            LOGGER.log_event("}}rbUnable to write approved nics to the registry!}}xx", log_level=1)
            return False
        
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
            w = wmi.WMI()
            net_configs = w.Win32_NetworkAdapterConfiguration()
            NetworkDevices._NIC_CONFIGURATION_CACHE = dict()
            for c in net_configs:
                i = c.InterfaceIndex
                if not i in NetworkDevices._NIC_CONFIGURATION_CACHE:
                    NetworkDevices._NIC_CONFIGURATION_CACHE[i] = []
                if c.IPAddress is not None:
                    NetworkDevices._NIC_CONFIGURATION_CACHE[i] += c.IPAddress

        ret = []
        # Find the list of addresses for this adapter if present
        if interface_index in NetworkDevices._NIC_CONFIGURATION_CACHE:
            ret = NetworkDevices._NIC_CONFIGURATION_CACHE[interface_index]

        return ret

    def get_nic_by_interface_index(interface_index):
        # Find the nic in question
        ret = None

        w = wmi.WMI()
        ifaces = w.Win32_NetworkAdapter(InterfaceIndex=interface_index)
        for iface in ifaces:
            ret = iface
        
        return ret


    @staticmethod
    def get_nics_w32():
        # Return a list of nics found in the system
        ret = []

        w = wmi.WMI()
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

        w = wmi.WMI(namespace="StandardCimv2")

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
    def list_system_nics():
        global LOGGER
        NetworkDevices.init_device_list()
        verbose = util.get_param(2, "").strip("-")
        if verbose == "verbose":
            verbose = "v"


        # Get a list of nics currently in the system
        nics_found = NetworkDevices.get_nics_w32()
        for nic in nics_found:
            (nic_name, nic_network_name, nic_ip_addresses, nic_connected, nic_enabled, attribs, iface, nic_if_index) = nic

            if nic_network_name != "None" and nic_network_name is not None:
                nic_network_name = "(}}yb" + "{0:>10}".format(nic_network_name) + "}}gn)"
            else:
                nic_network_name = "(" + "{0:>10}".format("None") + ")"

            if nic_ip_addresses is None:
                nic_ip_addresses = []
            
            if nic_connected is True:
                nic_connected = "(}}yb" + "{0:>12}".format("Connected") + "}}gn)"
            else:
                nic_connected = "(}}yn" + "{0:>12}".format("Disconnected") + "}}gn)"

            # 1-Up, 2-Down, 3-Testing
            if nic_enabled == 0:
                nic_enabled = "(}}ybEnabled}}gn)"
            elif nic_enabled == 22:
                nic_enabled = "(}}ynDisabled}}gn)"
            else:
                nic_enabled = "(}}rnMisConfigured}}gn)"
            
            approved_status = "(}}rb" + "{0:>12}".format("Not Approved") + "}}gn)"
            if NetworkDevices.is_nic_approved(nic_name, nic_ip_addresses):
                approved_status = "(}}mb" + "{0:>12}".format("Approved Nic") + "}}gn)"

            p("}}gn" + approved_status + " (ID: {0:>2}) ".format(nic_if_index) + \
                "{0:43}".format(nic_name) + \
                " " + nic_network_name + \
                " " + nic_connected + " " + nic_enabled + "}}xx")
            if len(nic_ip_addresses) > 0:
                p("   IP Addresses: " + str(nic_ip_addresses))
            if verbose == "v":
                p("-- " + str(attribs))

        return True
    @staticmethod
    def disable_nic(interface_index):
        w = wmi.WMI(namespace="StandardCimv2")

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
        w = wmi.WMI(namespace="StandardCimv2")

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
    def scan_nics():
        global LOGGER
        # May need to call this before calling this function so that COM works
        # pythoncom.CoInitialize() - called in the main function
        
        # Make sure device list is initialized
        NetworkDevices.init_device_list()

        LOGGER.log_event("scanning for unauthorized nics...", log_level=4)


        nic_list = NetworkDevices.get_nics_w32()

        for nic in nic_list:
            (nic_name, nic_network_name, nic_ip_addresses, nic_connected, nic_enabled, attribs, iface, nic_if_index) = nic
                        
            if NetworkDevices.is_nic_approved(nic_name, nic_ip_addresses):
                if nic_enabled == 22:
                    # Turn this nic on!
                    LOGGER.log_event("Approved nic is not enabled - turning on " + nic_name, log_level=1)
                    try:
                        #iface.Enable()
                        NetworkDevices.enable_nic(nic_if_index)
                    except Exception as ex:
                        LOGGER.log_event("** UNABLE TO ENABLE DEVICE: " + nic_name + "\n" + 
                            str(ex), log_level=1)

                # # Approved Nic!
                # if dev_id:
                #     # Enable this nic
                #     cmd = "netsh interface set interface \"" + dev_id + "\" admin=ENABLED"
                #     # print(cmd)
                #     os.system(cmd)
                # else:
                #     # Not plugged in?
                #     pass
                # pass
            else:
                if nic_enabled == 0:
                    # Nic is on and shouludn't be
                    LOGGER.log_event("UnApproved NIC Detected - Disabling " + nic_name, log_level=1)
                    try:
                        #iface.Enable()
                        NetworkDevices.disable_nic(nic_if_index)
                    except Exception as ex:
                        LOGGER.log_event("** UNABLE TO DISABLE DEVICE: " + nic_name + "\n" + 
                            str(ex), log_level=1)
                # # Device isn't in the approved list!
                # if dev_id:
                #     logging.info("     ---> !!! unauthorized !!!, disabling..." + str(dev_id))
                #     cmd = "netsh interface set interface \"" + dev_id + "\" admin=DISABLED"
                #     # print(cmd)
                #     os.system(cmd)
                # else:
                #     # Not authorized - but not plugged in?
                #     pass
    
        return True