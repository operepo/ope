import sys
import os
import wmi
import pythoncom
from win32com.shell import shell, shellcon

import util
from color import p


class Computer:
    # Master list of WMI connections - avoid reconnect for every call
    _WMI = dict()

    # Functions to help get information about the local computer
    # Win32_ComputerSystem - to get domain status, bios admin pw set, etc...
    # -- AdminPasswordStatus - shows as 3 on CTL laptop (unknown?)
    # -- PartOfDomain - Should check and be false - we don't support domains!
    # Win32_OperatingSystem


    #Win32_BIOS
    # - SerialNumber (SN of laptop - 96FW...0000710)
    # - Name - '3.00.00.CTL'
    # - BiosVersion - tuple of parts ('Intel - 2', '3.00.00.CTL', 'Phoenix Technologies LTD. - 12345678')
    # - Manufacturer - 'Pheonix Technologies LTD.' (LENOVO on work laptop)

    @staticmethod
    def create_win_shortcut(lnk_path, ico_path, target_path, description):
        ret = True

        # Remove old file
        if os.path.exists(lnk_path):
            os.unlink(lnk_path)

        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink,
            None,
            pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )
        shortcut.SetPath(target_path)
        shortcut.SetDescription(description)
        shortcut.SetIconLocation(ico_path, 0)
        persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        persist_file.Save(lnk_path, 0)

        return ret

    @staticmethod
    def get_wmi_connection(namespace="cimv2"):
        if namespace in Computer._WMI:
            return Computer._WMI[namespace]
        
        w = wmi.WMI(namespace=namespace)
        Computer._WMI[namespace] = w
        return w
    
    @staticmethod
    def get_disk_info():
        # Return information about disks in the system
        ret = dict()
        w = Computer.get_wmi_connection()

        partitions = w.Win32_DiskPartition()
        ret["disk_total_paritions"] = len(partitions)
        
        items = w.Win32_DiskDrive()
        ret["disk_count"] = len(items)
        for item in items:
            index = str(item.Index)
            key_header = "disk_" + index + "_"
            ret[key_header + "index"] = item.Index
            ret[key_header + "caption"] = item.Caption
            ret[key_header + "compression_method"] = item.CompressionMethod
            ret[key_header + "description"] = item.Description
            ret[key_header + "device_id"] = item.DeviceID
            ret[key_header + "firmware_revision"] = item.FirmwareRevision
            ret[key_header + "install_date"] = item.InstallDate
            ret[key_header + "interface_type"] = item.InterfaceType
            ret[key_header + "manufacturer"] = item.Manufacturer
            ret[key_header + "media_loaded"] = item.MediaLoaded
            ret[key_header + "media_type"] = item.MediaType
            ret[key_header + "model"] = item.Model
            ret[key_header + "name"] = item.Name
            ret[key_header + "partitions"] = item.Partitions
            ret[key_header + "pnp_device_id"] = item.PNPDeviceID
            ret[key_header + "serial_number"] = item.SerialNumber
            ret[key_header + "signature"] = item.Signature
            ret[key_header + "size"] = item.Size
            ret[key_header + "status"] = item.Status

            # List partition info for this disk
            for part in partitions:
                # If this partition is on the same disk, list it here
                disk_index = str(part.DiskIndex)
                if disk_index == index:
                    # Determine if this partition and therefore drive is the boot drive
                    boot_partition = part.BootPartition
                    if boot_partition:
                        ret[key_header + "boot_drive"] = boot_partition
                        ret["disk_boot_drive_serial_number"] = item.SerialNumber

                    part_index = str(part.Index)
                    part_header = "part_" + part_index + "_"
                    ret[key_header + part_header + "boot_partition"] = part.BootPartition
                    ret[key_header + part_header + "bootable"] = part.Bootable
                    ret[key_header + part_header + "caption"] = part.Caption
                    ret[key_header + part_header + "description"] = part.Description
                    ret[key_header + part_header + "device_id"] = part.DeviceID
                    ret[key_header + part_header + "disk_index"] = part.DiskIndex
                    ret[key_header + part_header + "index"] = part.Index
                    ret[key_header + part_header + "name"] = part.Name
                    ret[key_header + part_header + "primary_partition"] = part.PrimaryPartition
                    ret[key_header + part_header + "purpose"] = part.Purpose
                    ret[key_header + part_header + "size"] = part.Size
                    ret[key_header + part_header + "status"] = part.Status
                    ret[key_header + part_header + "system_name"] = part.SystemName
                    ret[key_header + part_header + "type"] = part.Type
    
        return ret

    @staticmethod
    def get_bios_info():
        # Get information about the system bios
        ret = dict()
        w = Computer.get_wmi_connection()

        # Get info about the BIOS
        items = w.Win32_BIOS()
        for item in items:
            ret['bios_serial_number'] = item.SerialNumber
            ret['bios_name'] = item.Name
            ret['bios_version'] = item.BiosVersion
            ret['bios_manufacturer'] = item.Manufacturer

        return ret
    
    @staticmethod
    def get_computer_system_info():
        # Return information about the computer system
        ret = dict()
        w = Computer.get_wmi_connection()

        # Get info about the computer
        items = w.Win32_ComputerSystem()
        for item in items:
            ret['cs_part_of_domain'] = item.PartOfDomain
            ret['cs_admin_password_status'] = item.AdminPasswordStatus
            ret['cs_caption'] = item.Caption
            ret['cs_domain'] = item.Domain
            ret['cs_model'] = item.Model
            ret['cs_number_of_logical_processors'] = item.NumberOfLogicalProcessors
            ret['cs_number_of_processors'] = item.NumberOfProcessors
            ret['cs_power_on_password_status'] = item.PowerOnPasswordStatus
            ret['cs_total_physical_memory'] = item.TotalPhysicalMemory
            ret['cs_workgroup'] = item.Workgroup
            ret['cs_bootup_state'] = item.BootupState
            ret['cs_dns_host_name'] = item.DNSHostName

        return ret
    
    @staticmethod
    def get_os_info():
        # Return information about the operating system
        ret = dict()
        w = Computer.get_wmi_connection()

        # Get info about the OS
        items = w.Win32_OperatingSystem()
        for item in items:
            ret['os_build_number'] = item.BuildNumber
            ret['os_name'] = item.Name  # item.Caption
            ret['os_caption'] = item.Caption
            ret['os_free_physical_memory'] = item.FreePhysicalMemory
            ret['os_free_space_in_paging_files'] = item.FreeSpaceInPagingFiles
            ret['os_free_virtual_memory'] = item.FreeVirtualMemory
            ret['os_install_date'] = item.InstallDate
            ret['os_last_boot_up_time'] = item.LastBootUpTime
            ret['os_local_date_time'] = item.LocalDateTime
            ret['os_number_of_users'] = item.NumberOfUsers
            ret['os_primary'] = item.Primary
            ret['os_registered_user'] = item.RegisteredUser
            ret['os_serial_number'] = item.SerialNumber
            ret['os_status'] = item.Status
            ret['os_system_device'] = item.SystemDevice
            ret['os_system_directory'] = item.SystemDirectory
            ret['os_system_drive'] = item.SystemDrive
            ret['os_total_virtual_memory_size'] = item.TotalVirtualMemorySize
            ret['os_total_visible_memory_size'] = item.TotalVisibleMemorySize
            ret['os_version'] = item.Version
            ret['os_windows_directory'] = item.WindowsDirectory

        return ret

    @staticmethod
    def get_machine_info(print_info=True):
        # Return information collected about this machine
        ret = dict()

        ret.update(Computer.get_bios_info())
        ret.update(Computer.get_computer_system_info())
        ret.update(Computer.get_os_info())
        ret.update(Computer.get_disk_info())

        # Print it nice
        if print_info:
            out = ""
            keys = sorted(ret.keys())
            for key in keys:
                out += key.ljust(35) + ": " + str(ret[key]) + "\n"

            p(out, debug_level=1)
        return ret

