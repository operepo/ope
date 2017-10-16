import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import sys
import logging

# Most event notification support lives around win32gui
import win32gui, win32gui_struct, win32con
GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"

logging.basicConfig(
    filename = 'c:\\ope-service.log',
    level = logging.DEBUG, 
    format = '[ope-service] %(levelname)-7.7s %(message)s'
)

class OPEService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'OPEService'
    _svc_display_name_ = 'OPEService'
    _svc_discription_ = "Open Prison Education Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
        #socket.setdefaulttimeout(60)
        
        socket.setdefaulttimeout(60)
        self.isAlive = True
        
        logging.info("service init")

        # register for a device notification - we pass our service handle
        # instead of a window handle.
        filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
                                        GUID_DEVINTERFACE_USB_DEVICE)
        self.hdn = win32gui.RegisterDeviceNotification(self.ssh, filter,
                                    win32con.DEVICE_NOTIFY_SERVICE_HANDLE)

    # Override the base class so we can accept additional events.
    def GetAcceptedControls(self):
        # say we accept them all.
        rc = win32serviceutil.ServiceFramework.GetAcceptedControls(self)
        rc |= win32service.SERVICE_ACCEPT_PARAMCHANGE \
              | win32service.SERVICE_ACCEPT_NETBINDCHANGE \
              | win32service.SERVICE_CONTROL_DEVICEEVENT \
              | win32service.SERVICE_ACCEPT_HARDWAREPROFILECHANGE \
              | win32service.SERVICE_ACCEPT_POWEREVENT \
              | win32service.SERVICE_ACCEPT_SESSIONCHANGE
        return rc
    
        # All extra events are sent via SvcOtherEx (SvcOther remains as a
    # function taking only the first args for backwards compat)
    def SvcOtherEx(self, control, event_type, data):
        # This is only showing a few of the extra events - see the MSDN
        # docs for "HandlerEx callback" for more info.
        if control == win32service.SERVICE_CONTROL_DEVICEEVENT:
            info = win32gui_struct.UnpackDEV_BROADCAST(data)
            msg = "A device event occurred: %x - %s" % (event_type, info)
        elif control == win32service.SERVICE_CONTROL_HARDWAREPROFILECHANGE:
            msg = "A hardware profile changed: type=%s, data=%s" % (event_type, data)
        elif control == win32service.SERVICE_CONTROL_POWEREVENT:
            msg = "A power event: setting %s" % data
        elif control == win32service.SERVICE_CONTROL_SESSIONCHANGE:
            # data is a single elt tuple, but this could potentially grow
            # in the future if the win32 struct does
            msg = "Session event: type=%s, data=%s" % (event_type, data)
        else:
            msg = "Other event: code=%d, type=%s, data=%s" \
                  % (control, event_type, data)

        logging.info("Event " + msg)
        servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0xF000, #  generic message
                (msg, '')
                )

                                    
    def SvcStop(self):
        self.isAlive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        self.isAlive = True
        logging.info("Service running")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()
        # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        # Write a stop message.
        logging.info("Service Stopped")
        servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (self._svc_name_, '')
                )


        
    def main(self):
        #f = open('D:\\test.txt', 'a')
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            # TODO

            # Grab screen shots

            # Grab event logs

            # Grab firewall logs

            # Run virus scanner

            # Security checks - is current user the correct user?

            # Is online?


            #f.write('Test Service  \n')
            #f.flush()
            #block for 24*60*60 seconds and wait for a stop event
            #it is used for a one-day loop
            rc = win32event.WaitForSingleObject(self.hWaitStop, 24*60*60*1000)
        #f.write('shut down \n')
        #f.close()
    
        #i = 0
        #while self.isAlive: 
        #    DataTransToMongo.run() //This is where my logic exists
        #
        #    time.sleep(86400)
        #
        #pass
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(OPEService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(OPEService)
