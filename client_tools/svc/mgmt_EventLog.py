#import servicemanager
import logging
import logging.handlers

import traceback

#from winsys import event_logs

from color import p, strip_color_codes, translate_color_codes
import util


class EventLog:
    _LOG_INSTANCES = dict()

    @staticmethod
    def get_current_instance(log_file=""):
        if len(EventLog._LOG_INSTANCES) < 1:
            # No log files initialized?
            p("}}rbNo Logger Setup!}}xx")
            return None
        
        if log_file == "":
            # Grab the first one?
            first_key = list(EventLog._LOG_INSTANCES.keys())[0]
            return EventLog._LOG_INSTANCES[first_key]

        if log_file in EventLog._LOG_INSTANCES:
            return EventLog._LOG_INSTANCES[log_file]

        # Couldn't find it!
        return None

    def __init__(self, log_file=None, service_name="OPEService"):
        EventLog._LOG_INSTANCES[log_file] = self
        #p("}}ynCreating Event Logger " + log_file + "/" + service_name)

        self.log_file = log_file
        self.service_name = service_name
        # Queue of messages - keep in the list until we get the log init properly?
        self.log_messages = []
        # Log levels = 1 - error(only), 2 - warnings, 3 - info, 4 - debug (all)
        self.log_level = 3
        self.logger = None
        self.init_logger()
        #self.log_event("Connected to Log: " + self.log_file + "/" + self.service_name)

    def init_logger(self):
        if self.logger is None:
            # Setup logging
            #p("}}gnInitializing logging....}}xx")
            try:
                logging.basicConfig(
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    format='[ope-svc] %(asctime)-15s %(levelname)-7.7s %(message)s'
                )
                        
                self.logger = logging.getLogger(self.service_name)
            except Exception as ex:
                p("}}rn*** Error setting up logger!}}xx\n" + str(ex))

            # Log to file if possible
            if self.log_file is None:
                p("}}rn*** No Log File Set! ***}}xx")
            else:
                try:
                    # Add file handler
                    f_handler = logging.FileHandler(self.log_file)
                    f_handler.setLevel(logging.DEBUG)
                    self.logger.addHandler(f_handler)
                except Exception as ex:
                    p("}}rbError setting up file logging!}}xx\n" + str(ex))
            
            # Log to win event log if possible
            try:
                if self.service_name == "OPEService":
                    dllname = "%programdata%\\ope\\Services\\OPEService\\OPEService.exe"
                else:
                    dllname = "%programdata%\\ope\\Services\\mgmt\\mgmt.exe"
                dllname = "%programdata%\\ope\\Services\\OPEService\\mgmt_EventLogMessages.dll"
                dllname = "%programdata%\\ope\\Services\\OPEService\\servicemanager.pyd"
                win_handler = logging.handlers.NTEventLogHandler(self.service_name, dllname, "Application")
                win_handler.setLevel(logging.DEBUG)
                self.logger.addHandler(win_handler)
            except Exception as ex:
                p("}}rbError setting up windows event logging!}}xx\n" + str(ex))

    def log_event(self, msg, is_error=False, show_in_event_log=True, log_level=3):
        self.init_logger()

        # Queue up messages - in case our logger isn't ready yet?
        if log_level > self.log_level:
            # Ignore this log item if we aren't at least level 5
            if self.log_level >= 5:
                p("}}ynSVC --> Skipping Log Event (Log Level " + str(log_level) +
                    "/" + str(self.log_level) + ")}}xx\n")
                p("\t" + msg)
            return


        # Remove }}rn?? type codes from the message - no need for them in text file or event log
        #msg = strip_color_codes(msg)
        msg = translate_color_codes(msg)
        msg_entry = dict(msg=msg, is_error=is_error, show_in_event_log=show_in_event_log)
        self.log_messages.append(msg_entry)

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
                p("}}rbError writing to service log! }}xx\n" + str(ex))
        else:
            # No logger? Print to the console
            p("(console) " + self.service_name + ": " + msg)

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
        #         p("}}rbError writing to win event log! }}xx\n" + str(ex))

        return