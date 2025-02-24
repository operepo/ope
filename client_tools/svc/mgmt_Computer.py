import time
from datetime import datetime
#import sys
import os
import wmi
import pythoncom
from win32com.shell import shell #, shellcon
import win32gui
import win32con
import ctypes
import win32api
import textwrap
import psutil



from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# Getting junk in logs from PIL - do this to stop it
import logging
pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)

import util
from color import p

from mgmt_RegistrySettings import RegistrySettings


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


    # STATE COLORS - Used for rendering state log (lock screen, background)
    # IDLE - Black - not working, not online
    STATE_IDLE_BG_COLOR = "#4d4c4c"
    STATE_IDLE_TEXT_COLOR = "#eeeeee"
    
    # WORKING - RED - Currently updating or syncing, don't unplug
    STATE_WORKING_BG_COLOR = "#b72313"
    STATE_WORKING_TEXT_COLOR = "#eeeeee"

    # DONE - Finished syncing, ready to pull plug and send back.
    STATE_DONE_BG_COLOR = "#00913a"
    STATE_DONE_TEXT_COLOR = "#eeeeee"

    LOG_BACKGROUND_COLOR = (200, 200, 200, int(255 * .20))
    #LOG_BACKGROUND_OPACITY = int(255 * .25)  # How transparent to make it

    # Where to save the image at
    STATE_RENDER_IMAGE_PATH = "%programdata%/ope/tmp/OPEState.png"

    # Where do we load the logo from?
    LOG_IMAGE_PATH = "%programdata%/ope/tmp/logo.png"

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

    @staticmethod
    def is_domain_joined():
        # Return True if the computer is joined to a domain
        info = Computer.get_computer_system_info()
        return info["cs_part_of_domain"]

    @staticmethod
    def render_lock_screen(image_path=None, header="", log_text=None, state="IDLE"):
        if image_path is None:
            image_path = Computer.STATE_RENDER_IMAGE_PATH # "%programdata%/ope/tmp/LockScreen.jpg"
        image_path = os.path.abspath(os.path.expandvars(image_path)).replace("\\", "/")

        logo_path = os.path.abspath(os.path.expandvars(Computer.LOG_IMAGE_PATH)).replace("\\", "/")

        # Default to IDLE
        background_color = Computer.STATE_IDLE_BG_COLOR
        text_color = Computer.STATE_IDLE_TEXT_COLOR
        state = state.upper()
        if state == "WORKING":
            background_color = Computer.STATE_WORKING_BG_COLOR
            text_color = Computer.STATE_WORKING_TEXT_COLOR
        elif state == "DONE":
            background_color = Computer.STATE_DONE_BG_COLOR
            text_color = Computer.STATE_DONE_TEXT_COLOR
                       
        if log_text is None:
            # No log text - try to load ope-state log file
            log_file_path = os.path.join(util.LOG_FOLDER, 'ope-state.log')
            log_file_fp = open(log_file_path, mode='r')
            log_text = log_file_fp.readlines() # read().split("\n")
            log_file_fp.close()
            # Grab the ope-state.log.1 file if it exists
            if os.path.exists(log_file_path+".1"):
                log_file_fp = open(log_file_path+".1", mode='r')
                log_text2 = log_file_fp.readlines()
                log_file_fp.close()
                log_text = log_text2 + log_text
                        
        if isinstance(log_text, str):
            # Split this string into a list
            log_text = log_text.split("\n")
        
        try:
            # Make sure we account for different DPI
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception as ex:
            p("ERROR setting DPI aware process " + str(ex))
        
        try:
            # Get full virtual screen dimensions (primary monitor)
            #l = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
            #t = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
            w = win32api.GetSystemMetrics(win32con.SM_CXFULLSCREEN) # SM_CXVIRTUALSCREEN)
            h = win32api.GetSystemMetrics(win32con.SM_CYFULLSCREEN) # SM_CYVIRTUALSCREEN)
        except Exception as ex:
            p("ERROR getting screen width and height, using default 1024x768" + str(ex))
            w = 1366  # 1366x768 is native for gen1 laptops 1024
            h = 768
        #p("Desktop Dimensions: " + str(w) + "/" + str(h), log_level=5)
        # Calculate Text Margins
        # 70% of height/width
        log_height = int(h * .7)
        log_width = int(w * .7)
        log_top = int(h/2 - log_height/2)
        log_bottom = log_top + log_height
        log_left = int(w/2 - log_width/2)
        log_right = log_left + log_width
        log_margin = 10 # pixels to draw off the edge
        log_line_spacing = 3
        log_background_color = Computer.LOG_BACKGROUND_COLOR

        # Make a new image
        i = Image.new('RGBA', (w, h), background_color)
        #i.putalpha(1)
        i_log = Image.new('RGBA', (log_width, log_height), log_background_color)
        log_draw = ImageDraw.Draw(i_log)

        font_file1 = "rc/STENCIL.ttf"
        font_file2 = "rc/consola.ttf"
        font_file3 = "rc/cour.ttf"
        font_file4 = "rc/courbd.ttf"
        font_large = ImageFont.truetype(os.path.join(util.APP_FOLDER, font_file1), 32)
        font_small = ImageFont.truetype(os.path.join(util.APP_FOLDER, font_file4), 14)
        font_xsmall = ImageFont.truetype(os.path.join(util.APP_FOLDER, font_file2), 12)
        draw = ImageDraw.Draw(i)

        # Load watermark
        wmark_path = os.path.join(util.APP_FOLDER, "rc/watermark.png")
        watermark_image = Image.open(wmark_path)
        #watermark_image.putalpha(1)

        # Draw the watermark
        wmark_x = int((log_width / 2) - (watermark_image.width / 2)) + log_left
        wmark_y = int((log_height / 2 + log_margin) - (watermark_image.height / 2)) + log_top
        #i.alpha_composite(watermark_image, (wmark_x, wmark_y))
        i.paste(watermark_image, (wmark_x, wmark_y), mask=watermark_image)
        #draw.image((wmark_x, wmark_y),  watermark_image)

        # Load the logo if it exists
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_image = logo_image.convert("RGBA")
            #Paste on the bottom corner of the log area
            i.alpha_composite(logo_image, 
                # Lower Right
                #(log_right - logo_image.width - log_margin, log_bottom + log_margin)
                # Upper Left
                (log_left + log_margin, log_top - logo_image.height - log_margin)
                )

        # Write Header
        if header is None or header == "":
            header = "OPE MAINTENANANCE LOG"
        
        # textsize deprecated
        #txt_w, txt_h = log_draw.textsize(header, font_large)
        txt_w = log_draw.textlength(header, font_large)
        (left, top, right, bottom) = font_large.getbbox("A")
        txt_h = bottom - top
        draw_x = (log_width/2) - (txt_w / 2)
        #draw_y = (h/2) - (txt_h / 2)
        draw_y = 10
        log_draw.text((draw_x, draw_y), header, text_color, font=font_large)

        # Draw the date/time
        dt_string = "Refreshed: " + datetime.now().strftime("%b %d, %Y    %I:%M %p") # %-I:%-M %p")
        import mgmt_CredentialProcess
        dt_string += " -- version " + mgmt_CredentialProcess.CredentialProcess.get_mgmt_version()
        #dt_w, dt_h = draw.textsize(dt_string, font_xsmall)
        dt_w = draw.textlength(dt_string, font_xsmall)
        (left, top, right, bottom) = font_xsmall.getbbox("A")
        dt_h = bottom - top
        dt_x = log_left + (log_width - dt_w - log_margin)
        dt_y = log_top - dt_h - log_margin
        draw.text((dt_x, dt_y), dt_string, text_color, font=font_xsmall)

        # Where does our log start?
        log_start_top = txt_h + log_margin + draw_y

        # Draw a seperator
        log_draw.line((0, log_start_top, w, log_start_top), fill="black", width=2)

        # Get the text height for log entries
        #log_text_width, log_text_height = draw.textsize("|", font_small)
        log_text_width = draw.textlength("|", font_small)
        (left, top, right, bottom) = font_small.getbbox("|")
        log_text_height = bottom - top

        # Calculate number of log lines based on this height w a small margin
        log_space_h = log_bottom - log_top - (log_margin*2)
        log_space_w = log_right - log_left - (log_margin*2)
        total_log_lines = int( log_space_h  / (log_text_height + (log_line_spacing) ) )
        #total_chars = int( (log_width - log_margin * 2 ) / (log_text_width) )
        total_chars = int( log_space_w / (log_text_width) )
        #p("W/H//LinesToDraw " + str(log_text_width) + "/" + str(log_text_height) + "//" + str(total_log_lines))
        # Flip log so newest is on top
        log_text.reverse()

        lines_to_draw = []
        for l in log_text:
            lines = textwrap.wrap(l, width=total_chars)
            for line in lines:
                lines_to_draw.append(line)
        
        #print("Dimensions: " + str(log_text_width) + "/" + str(log_text_height) + "/" + str(total_log_lines))
        # Shave off lines if there are too many (e.g. tail the log)
        while len(lines_to_draw) > total_log_lines - 1:
            # Remove first item (top entry)
            lines_to_draw.pop(0)
    
        # Render this line
        curr_h = log_start_top + log_margin
        for l in lines_to_draw:
            log_draw.text((log_margin, curr_h), l, text_color, font=font_small)
            curr_h += log_text_height + log_line_spacing

        # Render the log image on the main image
        i.alpha_composite(i_log, (log_left, log_top))

        # Render the lines in the log
        #txt = str(render_time)
        # txt_w, txt_h = draw.textsize(txt, font)
        # draw_x = (w/2) - (txt_w / 2)
        # draw_y = (h/2) - (txt_h / 2) + prev_txt_h
        # draw.text((draw_x, draw_y), txt, (255, 255, 255), font=font)
        #draw.text((300, 5), "Time Stamp: " + sshot_time, (255, 255, 255), font=font)

        # Add the current seconds to the filepath so we get unique lock screen images
        # d_name = os.path.dirname(image_path)
        # b_name = os.path.basename(image_path)
        # n, ext = os.path.splitext(b_name)
        # new_name = n + "." + str(render_time.second) + ext
        # image_path = os.path.join(d_name, new_name)
        
        # Save final image to tmp folder
        out = i.convert("P") # Convert to 256 color pallet (smaller image size)
        out.save(image_path, optimize=True)

        return image_path

    @staticmethod
    def render_desktop_background(image_path=None):
        if image_path is None:
            image_path = Computer.STATE_RENDER_IMAGE_PATH # "%programdata%/ope/tmp/LockScreen.jpg"
        image_path = os.path.abspath(os.path.expandvars(image_path)).replace("\\", "/")

        pass

    @staticmethod
    def get_desktop_image():
        r = ""
        try:
            r = win32gui.SystemParametersInfo(
                win32con.SPI_GETDESKWALLPAPER,
                None,
                0
            )
        except Exception as ex:
            p("Error getting desktop image: " + str(ex))
        return r
    
    @staticmethod
    def set_desktop_image(image_path=None):
        #SPI_SETDESKWALLPAPER = 20

        # Generate BMP file
        if image_path is None:
            image_path = Computer.STATE_RENDER_IMAGE_PATH # "%programdata%/ope/tmp/LockScreen.jpg"
        image_path = os.path.abspath(os.path.expandvars(image_path)).replace("\\", "/")

        try:
            #r = win32gui.SystemParametersInfo(
            win32gui.SystemParametersInfo(
                win32con.SPI_SETDESKWALLPAPER,
                image_path,
                1+2
                #win32con.SPIF_UPDATEINIFILE |
                #win32gui.SPIF_SENDWINDOWCHANGE

            )
        except Exception as ex:
            p("Error setting desktop image: " + str(ex))
        return None

    @staticmethod
    def set_lock_screen_image(image_path=None, kill_logon=True):
        if image_path is None:
            image_path = Computer.STATE_RENDER_IMAGE_PATH # "%programdata%/ope/tmp/LockScreen.jpg"
        image_path = os.path.abspath(os.path.expandvars(image_path)).replace("\\", "/")
        #print("Using image path: " + image_path)
        # Note - will return a new path/name w time in the filename
        #image_path = Computer.render_lock_screen(image_path)
        # Set reg key: Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP
        # add values for:
        # - DesktopImagePath -
        # - DesktopImageUrl -
        # - DesktopImageStatus - DWORD - 1
        # - LockScreenImagePath -
        # - LockScreenImageUrl - 
        # - LockScreenImageStatus - DWORD - 1
        # image resolution? (3840X2160)

        # NOTE - Need to flip / to \ in path or win won't show bitmap properly
        image_path = image_path.replace("/", "\\")

        RegistrySettings.set_reg_value(
            root="HKLM\\SOFTWARE",
            app="Microsoft\\Windows",
            subkey="CurrentVersion\\PersonalizationCSP",
            value_name="LockScreenImageStatus",
            value=1,
            value_type="REG_DWORD"
        )
        RegistrySettings.set_reg_value(
            root="HKLM\\SOFTWARE",
            app="Microsoft\\Windows",
            subkey="CurrentVersion\\PersonalizationCSP",
            value_name="LockScreenImagePath",
            value=image_path,
            value_type="REG_SZ"
        )
        RegistrySettings.set_reg_value(
            root="HKLM\\SOFTWARE",
            app="Microsoft\\Windows",
            subkey="CurrentVersion\\PersonalizationCSP",
            value_name="LockScreenImageUrl",
            value=image_path,
            value_type="REG_SZ"
        )

        # Turn of lock screen blur
        RegistrySettings.set_reg_value(
            root="HKLM\\SOFTWARE",
            app="Policies\\Microsoft",
            subkey="Windows\\System",
            value_name="DisableAcrylicBackgroundOnLogon",
            value=1,
            value_type="REG_DWORD"
        )

        # Tell logonui process to exit - forces refresh of lockscreen
        # NOTE - WMI not working when screen is locked? try psutil
        #w = Computer.get_wmi_connection()
    
        # # Get the processes
        # p_list = w.Win32_Process(Name="logonui.exe")
        # for p in p_list:
        #     # Kill the process so it refreshes the lock screen
        #     p_id = p.ProcessId
        #     p("Refreshing logonui.exe (terminating process) " + str(p_id))
        #     #r = p.Terminate()
        #     p.Terminate()

        if kill_logon is True:
            Computer.kill_process(ps_name="logonui.exe")
        
        return None

    @staticmethod
    def kill_process(ps_name=""):
        ret = False
        for ps in psutil.process_iter():
            name = str(ps.name())
            #print("PS Name: " + name)
            if name.lower() == ps_name.lower():
                p("Found " + ps_name + " - attempting to kill.", log_level=5)
                ps.kill()
                ret = True

        return ret

    @staticmethod
    def read_mbr(drive="\\\\.\\PhysicalDrive0", mbr_file="rc/gen2_laptop.mbr"):
        # Grab the MBR from the drive
        ret = False

        try:
            mbr_f = open(drive, 'rb')
            mbr_data = mbr_f.read(1)
            mbr_f.close()
        except Exception as ex:
            print("Unable to read MBR: " + str(drive) + "\n" + str(ex))
            return False
        
        try:
            dat_file = open(mbr_file, 'wb')
            dat_file.write(mbr_data)
            dat_file.close()
            ret = True
        except Exception as ex:
            print("Unable to write MBR data file: " + str(mbr_file) + "\n" + str(ex))
            return False

        return ret
    
    @staticmethod
    def write_mbr(drive="\\\\.\\PhysicalDrive0", mbr_file="rc/gen2_laptop.mbr"):
        # Save the MBR file to the drive
        ret = False

        try:
            dat_file = open(mbr_file, 'rb')
            mbr_data = dat_file.read(1)
            dat_file.close()
        except Exception as ex:
            print("Unable to open MBR data file: " + str(mbr_file) + "\n" + str(ex))
            return False

        try:
            mbr_f = open(drive, 'wb')
            mbr_f.write(mbr_data)
            mbr_f.close()
            ret = True
        except Exception as ex:
            print("Unable to write MBR data file: " + str(mbr_file) + "\n" + str(ex))
            return False

        return ret

    @staticmethod
    def test_code():
        # p_id = p.ProcessId
        # p_domain, p_ret, p_user = p.GetOwner()
        # print("P Owner: " + str(p_id) + " " + str(p_user))
        #Might need SeDebugPrivilege
        
        #0 is success
        # print("Ret Code: " + str(r))
        #Try sending ctrl + alt + del?
        #Doesn't work? Need run as service?
        #r = ctypes.windll.sas.SendSAS(0)
        #print("Ret Code: " + str(r))

        #Doesn't work.
        # Try turning on the screen saver?
        try:
            ss_timeout = win32gui.SystemParametersInfo(
                win32con.SPI_GETSCREENSAVETIMEOUT,
                0,
                0
            )
            if ss_timeout < 300:
                ss_timeout = 300 # 5 mins
            ss_timeout = 7200 # 2 hrs
            
            r = win32gui.SystemParametersInfo(
                win32con.SPI_SETSCREENSAVETIMEOUT,
                ss_timeout,
                win32con.SPIF_UPDATEINIFILE |
                win32con.SPIF_SENDWININICHANGE

            )
        except Exception as ex:
            print(ex)
            pass

        #print("Ret Code: " + str(r))
        pass


if __name__ == "__main__":
    pass
    # Do tests
    Computer.test_code()

    # while True:
    #     #Computer.set_lock_screen_image()
    #     Computer.render_lock_screen(
    #         header="Updating App",
    #         log_text=None, #["line 1", "line 2", "line 3", "line 4"],
    #         state="WORKING"
    #     )
    #     Computer.set_lock_screen_image()
    #     Computer.set_desktop_image()
    #     time.sleep(10)
    #     Computer.render_lock_screen(
    #         header="Update Done",
    #         log_text=None, #["line 1", "line 2", "line 3", "line 4", "line 1", "line 2", "line 3", "line 4"],
    #         state="DONE"
    #     )
    #     Computer.set_lock_screen_image()
    #     Computer.set_desktop_image()
    #     time.sleep(10)
    #     Computer.render_lock_screen(
    #         header="IDLE",
    #         log_text=None, #["line 1", "line 2", "line 3", "line 4", "line 1", "line 2", "line 3", "line 4"],
    #         state="IDLE"
    #     )
    #     Computer.set_lock_screen_image()
    #     Computer.set_desktop_image()
    #     time.sleep(10)
    pass
