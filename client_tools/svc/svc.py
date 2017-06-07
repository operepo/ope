import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import sys

class OPEService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'OPEService'
    _svc_display_name_ = 'OPEService'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
        socket.setdefaulttimeout(60)
        self.isAlive = True
        
    def SvcStop(self):
        self.isAlive = False
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        self.isAlive = True
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, 
                              servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
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
