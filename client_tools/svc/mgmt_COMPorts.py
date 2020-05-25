


class COMPorts:

    @staticmethod
    def scan_com_ports():
        # TODO - Need Debug
        # Use WMI to pull a list of com ports
        w = wmi.WMI()

        logging.info("Scanning USB/Serial COM Ports...")

        # Scan for PNP Devices that are ports
        for port in w.Win32_PNPEntity(PNPClass="Ports"):
            logging.info("PNP COM Port Found: " + str(port.name))
            if port.Status == "OK":
                # Port is on and working - turn it off
                logging.info("COM Port " + str(port.Caption) + " is on - disabling...")
                try:
                    port.Disable()
                except Exception as ex:
                    logging.info("ERROR!!! " + str(ex))
            else:
                logging.info("COM Port " + str(port.Caption) + " is off...")

        # Scan for Serial devices (may not be PNP)
        for port in w.Win32_SerialPort():
            print("Serial Port Found: " + str(port.name))
            if port.Status == "OK":
                logging.info("Serial Port " + str(port.Caption) + " is on - disabling...")
                try:
                    port.Disable()
                except Exception as ex:
                    logging.info("ERROR!!! " + str(ex))
            else:
                logging.info("Serial Port " + str(port.Caption) + " is off...")

        return
