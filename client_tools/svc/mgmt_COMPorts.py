
from color import p

from mgmt_Computer import Computer


class COMPorts:

    @staticmethod
    def scan_com_ports():
        # TODO - Need Debug
        # Use WMI to pull a list of com ports
        w = Computer.get_wmi_connection()

        p("Scanning USB/Serial COM Ports...")

        # Scan for PNP Devices that are ports
        for port in w.Win32_PNPEntity(PNPClass="Ports"):
            p("PNP COM Port Found: " + str(port.name))
            if port.Status == "OK":
                # Port is on and working - turn it off
                p("COM Port " + str(port.Caption) + " is on - disabling...")
                try:
                    port.Disable()
                except Exception as ex:
                    p("ERROR!!! " + str(ex))
            else:
                p("COM Port " + str(port.Caption) + " is off...")

        # Scan for Serial devices (may not be PNP)
        for port in w.Win32_SerialPort():
            print("Serial Port Found: " + str(port.name))
            if port.Status == "OK":
                p("Serial Port " + str(port.Caption) + " is on - disabling...")
                try:
                    port.Disable()
                except Exception as ex:
                    p("ERROR!!! " + str(ex))
            else:
                p("Serial Port " + str(port.Caption) + " is off...")

        return
