"""
    Widget to sit on the lock screen and show status of online/offline/syncing/updating/etc...
"""
import os
import sys
import time
import win32process
import win32ts

import util
from mgmt_EventLog import EventLog
global LOGGER
LOGGER = EventLog(os.path.join(util.LOG_FOLDER, 'ope-lockscreen.log'), service_name="OPELockScreen")

from mgmt_RegistrySettings import RegistrySettings
from mgmt_UserAccounts import UserAccounts

from color import p

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

#pyrcc5 lock_screen_widget.qrc -o lock_screen_widget_qrc.py
import lock_screen_widget_qrc

class AppWindow(QtWidgets.QWidget):
    def __init__(self):
        super(QtWidgets.QWidget, self).__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
            )

        self.current_user = UserAccounts.get_active_user_name()
        self.process_id = win32process.GetCurrentProcessId()
        self.session_id = win32ts.ProcessIdToSessionId(self.process_id)

        p("Active User: " + self.current_user + " " + str(self.session_id))

        tmp_folder = QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.TempLocation
            )

        # Make sure the app is only running once
        self.lock_file = QtCore.QLockFile(tmp_folder+"/ope_"+str(self.session_id)+".lock")
        if self.lock_file.tryLock():
            p("Lock Screen Widget: Running...")
            pass
        else:
            p("Lock Screen Widget: App already running!")
            #QtCore.QCoreApplication.exit()
            sys.exit()
            return

        layout = QtWidgets.QGridLayout(self)

        self.show_close_button = True
        if getattr(sys, 'frozen', False):
            # Running as an EXE - turn off the close button
            self.show_close_button = False

        # Get app icon
        self.app_icon = QtGui.QIcon(":/logo_icon.png")
        self.setWindowIcon(self.app_icon)
        
        # Connection images
        #img = QtGui.QImageReader(":/connection/online2.png")
        #img.setAutoTransform(True)
        #self.online_image = QtGui.QPixmap.fromImageReader(img)
        self.online_image = QtGui.QPixmap(":/connection/online.png")
        #print(self.online_image.isNull())
        

        #img = QtGui.QImageReader(":/connection/offline.png")
        #img.setAutoTransform(True)
        #self.offline_image = QtGui.QPixmap.fromImage(img.read())
        self.offline_image = QtGui.QPixmap(":/connection/offline.png")
        #print(self.offline_image.isNull())

        # State Images
        self.idle_images = []
        for i in range(0, 10):
            pm = QtGui.QPixmap(':/state/idle' + str(i) + '.png')
            self.idle_images.append(pm)
            #print('\t' + str(pm.isNull()))
        
        # Working Images
        self.working_images = []
        for i in range(0, 2):
            pm = QtGui.QPixmap(':/state/working' + str(i) + '.png')
            self.working_images.append(pm)

        #self.working_image = QtGui.QPixmap(":/state/working.png")
        #print(self.working_image.isNull())

        self.complete_images = []
        self.complete_images.append(QtGui.QPixmap(":/state/complete.png"))
        #print(self.complete_image.isNull())

        # Connection Image
        self.connection_state = QtWidgets.QLabel('Connection')
        self.connection_state.resize(64, 64)
        #self.connection_state.setScaledContents(True)
        #self.connection_state.setBackgroundRole(QtGui.QPalette.Base)
        self.connection_state.setPixmap(self.offline_image)
        #self.connection_state.resize(self.offline_image.width(), self.offline_image.height())
        layout.addWidget(self.connection_state, 0, 0, QtCore.Qt.AlignCenter)
        

        # State image (idle, working, complete)
        self.current_state_image = self.idle_images
        self.current_state_index = 0
        
        self.current_state = QtWidgets.QLabel('State')
        #self.current_state.setScaledContents(True)
        #self.current_state.setBackgroundRole(QtGui.QPalette.Base)
        self.current_state.setPixmap(self.current_state_image[self.current_state_index])
        layout.addWidget(self.current_state, 0, 1, QtCore.Qt.AlignCenter)
        
        self.current_state_title = QtWidgets.QLabel('')
        layout.addWidget(self.current_state_title, 1, 0, 1, 2, QtCore.Qt.AlignRight)

        self.last_sync_status = QtWidgets.QLabel('')
        layout.addWidget(self.last_sync_status, 2, 0, 1, 2, QtCore.Qt.AlignRight)

        self.version_label = QtWidgets.QLabel()
        self.version_label.setText("version:")
        layout.addWidget(self.version_label, 3, 0, 1, 2, QtCore.Qt.AlignRight)
      
        logs_pos = (4, 0, 1, 2)
        if self.show_close_button:
            self.close_button = QtWidgets.QPushButton('Close')
            self.close_button.clicked.connect(self.on_close)
            layout.addWidget(self.close_button, 4, 0)
            # Mmake the logs_pos only take 1 column if close button visible
            logs_pos = (4, 1, 1, 1)

        self.view_log_button = QtWidgets.QPushButton('Logs')
        self.view_log_button.clicked.connect(self.on_view_logs)
        self.view_log_button.setVisible(False)
        layout.addWidget(self.view_log_button, logs_pos[0], logs_pos[1], logs_pos[2], logs_pos[3])
        
        self.setWindowTitle("OPE Status")
        self.setFixedSize(220, 200)
        self.position_widget()

        # Do initial refresh of settings
        self.refresh_state_from_registry()

        # Animate the current state icon
        self.current_state_timer = QtCore.QTimer()
        self.current_state_timer.timeout.connect(self.animate_current_state)
        self.current_state_timer.setInterval(800)
        self.current_state_timer.start()

        # Load the state from the registry every few seconds
        self.refresh_state_from_registry_timer = QtCore.QTimer()
        self.refresh_state_from_registry_timer.timeout.connect(self.refresh_state_from_registry)
        self.refresh_state_from_registry_timer.setInterval(1500)
        self.refresh_state_from_registry_timer.start()
    
    def refresh_state_from_registry(self):
        # Read values from the registry.
        is_online = bool(RegistrySettings.get_reg_value(value_name="is_online", default=False))
        ope_state = RegistrySettings.get_reg_value(value_name="ope_state", default="IDLE").lower()
        ope_version = RegistrySettings.get_reg_value(value_name="ope_version", default="<unknown>")
        ope_state_title = RegistrySettings.get_reg_value(value_name="ope_state_title", default="")
        last_sync_lms_app_message = RegistrySettings.get_reg_value(value_name="last_sync_lms_app_message", default="<not synced yet>")

        # Set connection state
        if is_online is True:
            self.connection_state.setPixmap(self.online_image)
        else:
            self.connection_state.setPixmap(self.offline_image)

        # Set work state
        if ope_state == "done" or ope_state == "complete":
            self.current_state_image = self.complete_images
        elif ope_state == "working":
            self.current_state_image = self.working_images
        else:  # IDLE
            # Everything else counts as idle
            self.current_state_image = self.idle_images
        
        # Get the current mgmt verion
        self.version_label.setText("version: " + ope_version)
        self.current_state_title.setText(ope_state_title)
        self.last_sync_status.setText(last_sync_lms_app_message)
        return
    
    def animate_current_state(self):
        
        i = self.current_state_index
        images = self.current_state_image
        max_len = len(images)

        i += 1
        if i >= max_len:
            i = 0
        #print("Timer: " + str(i))
        self.current_state_index = i

        self.current_state.setPixmap(images[i])

        pass

    def position_widget(self):
        screen_w, screen_h = self.screen_size()

        x = screen_w - self.width()
        y = 0
        self.move(x, y)
    
    def screen_size(self):
        #screen = this.primaryScreen()
        #size = screen.size()
        #rect = screen.availableGeometry()
        size = QtWidgets.QDesktopWidget().screenGeometry(0)
        return (size.width(), size.height())

    def on_view_logs(self):
        # Show logs dialog.
        msg = QtWidgets.QMessageBox()
        msg.setText("LOGS")
        msg.exec_()

    def on_close(self):
        self.close()
        p("Closing...")


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = AppWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()



# ------------------------------------------------------

# import os
# import util
# from mgmt_EventLog import EventLog
# global LOGGER
# LOGGER = EventLog(os.path.join(util.LOG_FOLDER, 'ope-mgmt.log'), service_name="OPE")

# # Getting junk in logs from PIL - do this to stop it
# import logging
# pil_logger = logging.getLogger('PIL')
# pil_logger.setLevel(logging.INFO)

# from color import p

# from tkinter import *
# from PIL import ImageTk,Image


# class LScreenApp():
#     def __init__(self):
#         self.canvas = None
#         self.state_image = None
#         self.root = None
#         self.margin = 0
#         self.screen_width = 0
#         self.screen_height = 0
#         self.widget_width = 500
#         self.widget_height = 300
#         self.x = 0
#         self.y = 0
#         self.refresh_delay = 30000

#         self.init_app()
#         self.root.mainloop()
    
#     def init_app(self):
#         self.root = Tk()
#         self.root.title("OPE Status")
#         self.screen_width = self.root.winfo_screenwidth()
#         self.screen_height = self.root.winfo_screenheight()

#         # Take up full top portion of the screen
#         self.widget_width = self.screen_width
#         # Lets do top 1/3rd of the screen
#         self.widget_height = int(self.screen_height / 3)

#         self.root.geometry("%dx%d+%d+%d" % (
#             self.widget_width,
#             self.widget_height,
#             0,
#             0
#             ))
#         self.root.configure(background="grey")

#         # Get the rendered image
#         self.canvas = Canvas(self.root, width=self.widget_width, height=self.widget_height)
#         self.canvas.pack(fill="both", expand=True)
#         self.render_canvas()
        
#         self.root.lift()

#         #root.attributes('-topmost', True)
#         self.root.call('wm', 'attributes', '.', '-topmost', True)
#         self.root.update()        

#     def render_canvas(self):
#         try:
#             i = Image.open(os.path.expandvars("%programdata%\\ope\\tmp\\OPEState.png"))
#             ratio = i.width / self.widget_width # i.width / i.height
#             i = i.resize((self.widget_width, int(i.height * ratio)), Image.LANCZOS)
#             self.state_image = ImageTk.PhotoImage(i)
#             self.canvas.create_image(0, 0, anchor=NW, image=self.state_image)
#         except Exception as ex:
#             p("Error loading OPEState.png " + str(ex))
        
#         # Make sure this runs again soon
#         self.root.after(self.refresh_delay, self.render_canvas)

   

# if __name__ == "__main__":
#     app = LScreenApp()
