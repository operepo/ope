import sys
import os
import servicemanager
import logging
import logging.handlers
import weakref

import traceback

#from winsys import event_logs

import util


class EventLog:
    # The singleton instance of our logger class
    _LOG_INSTANCE = None
    _OPE_STATE_LOG_INSTANCE = None
    
    @staticmethod
    def get_current_instance():
        if EventLog._LOG_INSTANCE is None:
            # Invalid log instance!
            #print("No Logger Setup!")
            return None

        return EventLog._LOG_INSTANCE
    
    @staticmethod
    def get_ope_state_instance():
        if EventLog._OPE_STATE_LOG_INSTANCE is None:
            # Make the state logger and set it up.
            # NOTE - this is to log to the background of the OPE laptops
            lf = os.path.join(util.LOG_FOLDER, 'ope-state.log')  #"%programdata%\ope\tmp\log\ope-state.log"
            l = logging.getLogger("OPE_STATE")
            l.setLevel(logging.DEBUG)

            fmt = logging.Formatter('%(asctime)-15s %(message)s',
                '%Y-%m-%d %I:%M:%S%p')

            f_handler = logging.handlers.RotatingFileHandler(os.path.expandvars(lf),
                mode='a', maxBytes=2*1024, backupCount=1, delay=0, encoding=None)
            f_handler.setFormatter(fmt)
            f_handler.setLevel(logging.DEBUG)
            l.addHandler(f_handler)
            # Make flush of logs available
            l.flush = f_handler.flush

            EventLog._OPE_STATE_LOG_INSTANCE = l
            
        return EventLog._OPE_STATE_LOG_INSTANCE

    def __init__(self, log_file=None, service_name="OPEService"):
        EventLog._LOG_INSTANCE = self

        #print("Creating Event Logger " + log_file + "/" + service_name)

        self.log_file = log_file
        self.service_name = service_name
        # Queue of messages - keep in the list until we get the log init properly?
        self.log_messages = []
        # Queue for win messages - save up and log at the end
        self.log_messages_win = []

        # Log levels = 1 - error(only), 2 - warnings, 3 - info, 4 - debug (all)
        self.log_level = 3
        self.logger = None

        # Setup the destructor
        self._finalizer = weakref.finalize(self, self.flush_win_logs,
            self.log_messages_win)

        if self.init_logger() is False:
            print("***** MAJOR ERROR - Couldn't init logging! *****")
        #self.log_event("Connected to Log: " + self.log_file + "/" + self.service_name)

    def init_logger(self):
        if self.logger is None:
            
            # Setup logging
            #print("Initializing logging....")
            try:
                # Don't do basicConfig - it auto creates a streamhandler
                # logging.basicConfig(
                #     level=logging.DEBUG,
                #     datefmt='%Y-%m-%d %H:%M:%S',
                #     format='[ope-svc] %(asctime)-15s %(levelname)-7.7s %(message)s',
                #     filename=self.log_file
                # )
                        
                self.logger = logging.getLogger()
                self.logger.setLevel(logging.DEBUG)
                #self.logger.setFormatter(fmt)

            except Exception as ex:
                print("*** Error setting up logger!\n" + str(ex))
                return False

            self.add_file_handler()
            
            
            # Add a stream handler so it outputs on the screen
            # sh = logging.StreamHandler()
            # sh.setFormatter(fmt)
            # sh.setLevel(logging.DEBUG)
            # self.logger.addHandler(sh)
            # NOTE - this got moved to flush_win_logs so we
            # can dump them all in one shot instead of seperate events
            # Log to win event log if possible
            # try:
            #     #if self.service_name == "OPEService":
            #     #    dllname = "%programdata%\\ope\\Services\\OPEService\\OPEService.exe"
            #     #else:
            #     #    dllname = "%programdata%\\ope\\Services\\mgmt\\mgmt.exe"
            #     #dllname = "%programdata%\\ope\\Services\\OPEService\\mgmt_EventLogMessages.dll"
            #     #dllname = "%programdata%\\ope\\Services\\OPEService\\servicemanager.pyd"
            #     dllname = None

                
                
            #     win_handler = logging.handlers.NTEventLogHandler(self.service_name,
            #         dllname, "Application")
            #     win_handler.setFormatter(fmt)
            #     win_handler.setLevel(logging.DEBUG)

            #     self.logger.addHandler(win_handler)
            # except Exception as ex:
            #     print("Error setting up windows event logging!\n" + str(ex))
        
        return True

    def add_file_handler(self, log_file=None, fallback_log_file="%tmp%/mgmt.log"):
        if self.logger is None:
            # No logger!
            print("No logger present, can't add file handler!")
            return False
        
        fmt = logging.Formatter('[' + self.service_name + '] %(asctime)-15s %(levelname)-7.7s %(message)s',
            '%Y-%m-%d %H:%M:%S')

        # Get the current log file to try
        # 1st - current log_file param 
        # 2nd - self.log_file
        # 3rd - fallback log file
        lf = log_file
        if lf is None:
            lf = self.log_file
        if lf is None:
            lf = fallback_log_file
        # Collect error messages
        errors = []
        failed_lf = ""
        
        # Try the current log file
        try:
            f_handler = logging.handlers.RotatingFileHandler(os.path.expandvars(lf),
                mode='a', maxBytes=3*1024*1024, backupCount=1, delay=0, encoding=None)
            f_handler.setFormatter(fmt)
            f_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(f_handler)
            return True
        except Exception as ex:
            errors.append("S1 - Unable to add file handler " + str(lf) + "\n" + str(ex))
            failed_lf = lf
        
        if lf == fallback_log_file:
            # No more to try!
            # If we get here, we can't log
            print("-- Error setting up file logging! " + \
                str(lf) + "\n" + str(errors))
            return False

        # Try the next log file - try self.logfile
        lf = self.log_file
        if lf is None:
            # Skip to fallback
            lf = fallback_log_file
        # Try the current log file
        try:
            f_handler = logging.handlers.RotatingFileHandler(os.path.expandvars(lf),
                mode='a', maxBytes=3*1024*1024, backupCount=1, delay=0, encoding=None)
            f_handler.setFormatter(fmt)
            f_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(f_handler)
            return True
        except Exception as ex:
            errors.append("S2 - Unable to add file handler " + str(lf) + "\n" + str(ex))
            failed_lf = lf

        if lf == fallback_log_file:
            # No more to try!
            # If we get here, we can't log
            print("-- Error setting up file logging! " + \
                str(lf) + "\n" + str(errors))
            return False

        # Try the fallback
        lf = fallback_log_file
        # Try the current log file
        try:
            f_handler = logging.handlers.RotatingFileHandler(os.path.expandvars(lf),
                mode='a', maxBytes=3*1024*1024, backupCount=1, delay=0, encoding=None)
            f_handler.setFormatter(fmt)
            f_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(f_handler)
            return True
        except Exception as ex:
            errors.append("S3 - Unable to add file handler " + str(lf) + "\n" + str(ex))
            failed_lf = lf
        
        # If we get here, we can't log
        print("-- Error setting up file logging! " + \
                        str(lf) + "\n" + str(errors))
        
        return False

    
    def log_event(self, msg, is_error=False, show_in_event_log=True, log_level=3):
        self.init_logger()

        # Queue up messages - in case our logger isn't ready yet?
        if log_level > self.log_level:
            # Ignore this log item if we aren't at least level 5
            # if self.log_level >= 5:
            #     print("SVC --> Skipping Log Event (Log Level " + str(log_level) +
            #         "/" + str(self.log_level) + ")\n")
            #     print("\t" + msg)
            return


        # Remove }}rn?? type codes from the message - no need for them in text file or event log
        #msg = strip_color_codes(msg)
        #msg = translate_color_codes(msg)
        msg_entry = dict(msg=msg, is_error=is_error, show_in_event_log=show_in_event_log)
        self.log_messages.append(msg_entry)
        self.log_messages_win.append(msg_entry)

        # If there are messages waiting, log them.
        m_queue = self.log_messages.copy()
        self.log_messages.clear()

        if self.logger:
            try:
                for m in m_queue:
                    if m["is_error"]:
                        self.logger.error(m["msg"])
                    else:
                        self.logger.info(m["msg"])
            except Exception as ex:
                print("Error writing to service log!\n" + str(ex))
        else:
            # No logger? Print to the console
            print("(console) " + self.service_name + ": " + msg)

        # if self.win_logger:
        #     try:
        #         for m in m_queue:
        #             if m["show_in_event_log"]:
        #                 if m["is_error"]:
        #                     self.win_logger.log_event(type="error", message=m["msg"])
        #                     #servicemanager.LogMsg(
        #                     #    servicemanager.EVENTLOG_ERROR_TYPE,
        #                     #    0xF000,  # generic message
        #                     #    (m["msg"], '')
        #                     #)

        #                 else:
        #                     self.win_logger.log_event(type="information", message=m["msg"])
        #                     # servicemanager.LogMsg(
        #                     #     servicemanager.EVENTLOG_INFORMATION_TYPE,
        #                     #     0xF000,  # generic message
        #                     #     (m["msg"], '')
        #                     # )
        #     except Exception as ex:
        #         print("Error writing to win event log!\n" + str(ex))

        return
    
    def flush_win_logs(self, lines=None):
        #print("Flush_win_logs_called")
        # Flush the current logs to the win event logger
        #print("Flushing win logs")
        if lines is None:
            lines = self.log_messages_win
        if lines is None:
            print("NO WIN LOG LINES FOUND!")
            return False

        if len(lines) < 1:
            # Nothing to log?
            #print("No Lines?!")
            return True

        cp_lines = lines.copy()
        lines.clear()

        # Build up the output from the logs
        output = ""
        for line in cp_lines:
            l = line["msg"].strip()
            # Line might be packed together, split it out and then re-combine so it looks
            # correct in event log
            new_txt = ""
            parts = l.split("\n")
            for p in parts:
                new_txt += p.strip() + "\r\n"

            output += new_txt
            #output += line["msg"].strip() + "\r\n"

        #print(output)
        try:
            #servicemanager.SetEventSourceName("OPE")
            servicemanager.Initialize(self.service_name,
                "%programdata%\\ope\\Services\\OPEService\\servicemanager.pyd")
        except Exception as ex:
            print("Error setting source name for event logs!\n" + str(ex))

        try:
            # servicemanager.LogMsg(
            #     servicemanager.EVENTLOG_INFORMATION_TYPE,
            #     0xF000,  # generic message
            #     (output, '')
            # )
            servicemanager.LogInfoMsg(output)
        except Exception as ex:
            print("Error writing to windows event log!\n" +
                str(ex))
        
        return True
        
