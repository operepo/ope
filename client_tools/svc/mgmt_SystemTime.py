import os
import sys
import time

import wmi

from mgmt_RegistrySettings import RegistrySettings

from color import p

class SystemTime:

    @staticmethod
    def is_time_to_sync():
        # How long has it been since we synced our time?
        last_time_sync = RegistrySettings.get_reg_value(value_name="last_ntp_sync", default=0)
        curr_time = time.time()

        # Only sync every 5 minutes
        if curr_time - last_time_sync > 300:
            return True
        
        return False

    @staticmethod
    def sync_time_w_smc():
        # Do http request off smc to get the server date/time
        new_dt = time.time()

        # Set the time using WMI interface
        w = wmi.WMI()

        operating_systems = w.Win32_OperatingSystem()
        for o in operating_systems:
            p("}}gnSetting time to " + str(new_dt) + "...}}xx", debug_level=3)
            ret = o.SetDateTime(str(new_dt))
            if ret == 0:
                p("}}gnSuccess!}}xx", debug_level=3)
            else:
                p("}}rnError! " + str(ret) + "}}xx", debug_level=1)
        


    @staticmethod
    def sync_time_w_ntp():
        if not SystemTime.is_time_to_sync():
            p("}}gnNot time to sync w NTP servers yet, skipping.}}xx", log_level=4)
            return True

        RegistrySettings.set_reg_value(value_name="last_ntp_sync", value=time.time())
        
        smc_url = RegistrySettings.get_reg_value(value_name="smc_url", default="https://smc.ed")
        smc_host = smc_url.lower().replace("https://", "").replace("http://", "").replace("/", "")
        if ":" in smc_host:
            # port :8000 - remove it
            pos = smc_host.index(":")
            smc_host = smc_host[:pos]

        # Pull the current time from the SMC server and set it locally.
        # HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\DateTime\Servers
        # w32tm /stripchart /computer:smc.ed /dataonly /samples:5
        # w32tm /query /peers

        # Add our time servers to the list
        os.system("w32tm /config /update /manualpeerlist:\"" + smc_host + " time.windows.com 202.5.222.1\"")
        # Force the update
        os.system("w32tm /resync /nowait")  # /nowait

        return True