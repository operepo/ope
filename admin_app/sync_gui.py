from __future__ import print_function

import json
import socket
import os
import requests
import re
from functools import partial
import sys
from os.path import expanduser
import logging
import color
import router_utils
import socket
import traceback
import datetime
from datetime import timezone
from dateutil.parser import parse as parsedate

from util import markdown_to_bbcode, get_app_folder, get_home_folder, get_human_file_size, APP_FOLDER

# try glew + gles or sdl2?
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"  # "glew" # "angle_sdl2"  # gl, glew, sdl2, angle_sdl2, mock
os.environ["KIVY_GRAPHICS"] = "gles"  # "gles"
# os.environ["KIVY_GL_DEBUG"] = "1"
# os.environ["USE_SDL2"] = "1"
# os.environ["KIVY_WINDOW"] = "sdl2"  # "sdl2" "pygame"
# os.environ["KIVY_IMAGE"] = "sdl2"  # img_tex, img_dds, img_sdl2, img_ffpyplayer, img_gif, img_pil
# os.environ["KIVY_TEXT"] = "sdl2"

APP_RUNNING = True
# LOAD THIS VERSION
APP_VERSION = "0.0"

# Run as app starts to make sure we save the current app folder
# in response to issue #6
APP_FOLDER = get_app_folder()
print("APP FOLDER " + APP_FOLDER)

VERSION_FILE = os.path.join(APP_FOLDER, "version.json")
if os.path.isfile(VERSION_FILE):
    try:
        f = open(VERSION_FILE, "r")
        json_str = f.read()
        f.close()
        j_arr = json.loads(json_str)
        APP_VERSION = j_arr['version']
    except:
        APP_VERSION = "ERR"


from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'fbo', 'software')
Config.set('kivy', 'log_level', 'debug')  # ''trace', 'debug')

# [kivy]
# log_level = info
# log_enable = 1
# log_dir = logs
# log_name = kivy_%y-%m-%d_%_.txt
# log_maxfiles = 100
# Config.set('KIVY_GRAPHICS', 'gles')
# Adjust kivy config to change window look/behavior
# Config.set('graphics','borderless',1)
# Config.set('graphics','resizable',0)
# Config.set('graphics','position','custom')
# Config.set('graphics','left',500)
# Config.set('graphics','top',10)

# Config.set('graphics', 'resizeable', '0')
# Config.set('graphics', 'borderless', '1')



import uuid
import subprocess
import stat

from security import Enc

import threading
import time
from datetime import datetime, timedelta

# from gluon import DAL, Field
# from gluon.validators import *

import kivy

if 'KIVY_DATA_DIR' in os.environ:
    print("KIVY_DATA_DIR " + os.environ['KIVY_DATA_DIR'])
if 'KIVY_MODULES_DIR' in os.environ:
    print("KIVY_MODULES_DIR " + os.environ['KIVY_MODULES_DIR'])
if 'KIVY_HOME' in os.environ:
    print("KIVY_HOME " + os.environ['KIVY_HOME'])
if 'KIVY_SDL2_PATH' in os.environ:
    print("KIVY_SDL2_PATH " + os.environ['KIVY_SDL2_PATH'])
if 'PYTHONPATH' in os.environ:
    print("PYTHONPATH " + os.environ['PYTHONPATH'])
for p in sys.path:
    print("P " + str(p))

from kivy.app import App
from kivy.base import EventLoop
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.clock import mainthread
#from kivy.clock import ClockBase
from kivy.factory import Factory
from kivy.network.urlrequest import UrlRequest
from kivy.uix.label import Label
from scrolllabel import ScrollLabel
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.recycleview import RecycleView
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.settings import SettingString
from kivy.uix.settings import SettingItem
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty, OptionProperty
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooser, FileChooserListView, FileChooserIconView, FileSystemAbstract
kivy.require('1.10.1')


from widgets import ThreadSafePopup

# Add this path to the resources path
kivy.resources.resource_add_path(APP_FOLDER)
# [CRITICAL] [Clock       ] Warning, too much iteration done before the next frame. Check your code, or increase the Clock.max_iteration attribute
# Clock.max_iteration = 20
Window.size = (1000, 650)
# Window.borderless = True

# Git Repos to pull
GIT_REPOS = {"sysprep_scripts": "https://github.com/operepo/sysprep_scripts.git",
             "ope": "https://github.com/operepo/ope.git",
             "ope_laptop_binaries": "https://github.com/operepo/ope_laptop_binaries.git",
             "ope_server_sync_binaries": "https://github.com/operepo/ope_server_sync_binaries.git",
             }


# Import SSH stuff
import ssh_utils
from ssh_utils import FogSFTPFileSystem, FogDownloadFileSystem


# Manage multiple screens
sm = ScreenManager()
# Keep a reference to the main window
MAIN_WINDOW = None

# Find the base folder to store data in - use the home folder
BASE_FOLDER = os.path.join(get_home_folder(), ".ope")
# Make sure the .ope folder exists
if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER, 0o770)

# Progress bar used by threaded apps
progress_widget = None
progress_widget_label = None
sftp_progress_widget = None
sftp_progress_message = None
sftp_progress_last_update = time.time()



class LoginScreen(Screen):
    def do_login(self, loginText, passwordText):
        Logger.info("Logging in: " + loginText)
        # app = App.get_running_app()
        #
        # app.username = loginText
        # app.password = passwordText
        #
        # self.manager.transition = SlidTransition(direction="left")
        # self.manager.current = "connected"
        #
        # app.config.read(app.get_application_config())
        # app.config.write()

    def reset_form(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""
    pass


# === Password Box (masked ***) ===
class PasswordLabel(Label):
    pass


# Class to show a password box in the settings area
class SettingPassword(SettingString):
    def _create_popup(self, instance):
        super(SettingPassword, self)._create_popup(instance)
        self.textinput.password = True

    def add_widget(self, widget, *largs):
        if self.content is None:
            super(SettingString, self).add_widget(widget, *largs)
        if isinstance(widget, PasswordLabel):
            return self.content.add_widget(widget, *largs)


# Class to add a button to the settings area
class SettingButton(SettingItem):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        buttons = kwargs.pop('buttons')
        super(SettingItem, self).__init__(**kwargs)
        # super(SettingItem, self).__init__(title=kwargs['title'], panel=kwargs['panel'], key=kwargs['key'],
        #                                  section=kwargs['section'])
        for aButton in buttons: # kwargs["buttons"]:
            oButton = Button(text=aButton['title'], font_size='15sp')
            oButton.ID = aButton['id']
            self.add_widget(oButton)
            oButton.bind(on_release=self.On_ButtonPressed)

    def set_value(self, section, key, value):
        # Normally reads the config parser, skip here
        return

    def On_ButtonPressed(self, instance):
        self.panel.settings.dispatch('on_config_change', self.panel.config, self.section, self.key, instance.ID)

# Class for showing the password popup
class PasswordPopup(Popup):
    # Password function that will be called when the pw is set
    pw_func = None
    pass

# </editor-fold>


class MainWindow(BoxLayout):

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

    def on_touch_up(self, touch):
        # Logger.info("main.py: MainWindow: {0}".format(touch))
        pass


class SyncOPEApp(App, EventDispatcher):
    APP_VERSION = APP_VERSION
    # URL to download fog images from
    ope_fog_images_url = "http://dl.correctionsed.com/ope_lt_images"
    # URL where resources are located (e.g. gcf learnfree www files)
    ope_resources_url = "http://dl.correctionsed.com/ope_resources"
    server_mode = 'online'  # Start in online mode?

    def run_gcf_dl_test(self):
        gcf_url_path = "http://dl.correctionsed.com/ope_resources/gcflearnfree/gcf.zip"
        gcf_zip_file_path = "C:\\Users\\ray\\Desktop\\git_projects\\ope\\ope\\volumes\\gcf\\zip\\gcf.test.zip"

        dl_thread = self.start_www_download(gcf_url_path, gcf_zip_file_path)
        print("Started thread: " + str(dl_thread))
        ret = self.wait_for_www_download(dl_thread)
        if ret == "Complete":
            # Success!
            #status_label.text += "[b]Download Complete![/b]"
            print("DL Complete!")
        else:
            # Error!
            # status_label.text += "[b]Download Error![/b] - " + ret
            print("DL FAILED!")
        return ret

    def run_thread_safe_popup_test(self, title, message):
        pu = ThreadSafePopup()
        pu.set_title(title)
        pu.set_message(message)
        #pu.hide_ok()
        pu.hide_progress()
        #pu.hide_cancel()
        pu.open()

    def run_ssh_connect_test(self):
        ssh_utils.remove_server_from_known_hosts("192.168.10.25")
        return
        # Connect using saved credentials in current mode (online or offline)
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection()
        if ssh is None:
            print("Error making ssh connection!")
            return
        else:
            print("SSH Connected!")

        # Connect to OPE dl server
        ssh_server = "dl.correctionsed.com"
        ssh_user = "ray"
        ssh_pass = "testpassword"

        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection(
            ssh_server=ssh_server, ssh_user=ssh_user, ssh_pass=ssh_pass
        )

        if ssh is None:
            print("ERROR! " + err_str)
            return


        sftp = ssh.open_sftp()

        local_file = "C:\\Users\\ray\\Desktop\git_projects\\ope\\ope\\volumes\\fog\\images\\test_image.fog_image"
        #print(os.path.isfile(local_file))
        local_f = open(local_file, 'rb')
        
        start_time = time.time()
        end_time = 0

        remote_folder = "/home/ray/web/ope_lt_images/"
        remote_file = os.path.join(remote_folder, "test_image.fog_image").replace("\\", "/")

        print("Remote Folder: " + remote_folder)
        print(sftp.listdir("."))

        print("Pushing image: " + str(local_file) + " -> " + remote_file)

        try:
            # bufsize=8192
            with sftp.open(remote_file, mode="wb") as remote_f:
                print("opened")

        except Exception as ex:
            print("ERROR: " + str(ex))
            traceback.print_exc()

        
        print("Done pushing.")


    def run_tests(self):
        # Place to run tests from
        ret = True

        # Run dl in a different thread
        #gcf_thread = threading.Thread(target=self.run_gcf_dl_test, args=()).start()

        # popup_thread = threading.Thread(target=self.run_thread_safe_popup_test, args=('Copying', 'Copying files, please wait...')).start()

        self.run_ssh_connect_test()
        
        return ret

    def is_debug(self):
        ret = True

        # Check to see if the app is frozen (exe) to determine
        # if we are running in code or release
        if getattr(sys, 'frozen', False):
            # Running in pyinstaller bundle
            ret = False
        
        return ret

    def set_online_button_states(self, online_button, offline_button):
        # print("online state")
        if SyncOPEApp.server_mode == 'online':
            online_button.state = 'down'
            offline_button.state = 'normal'
        else:
            online_button.state = 'normal'
            offline_button.state = 'down'

    def on_online_server_button_state(self, instance, value):
        print("online_button_state" + str(value))

    def is_online(self):
        if SyncOPEApp.server_mode == 'online':
            return True
        else:
            return False

    use_kivy_settings = False

    required_apps = ["ope-gateway", "ope-dns", "ope-redis",
        "ope-postgresql", "ope-ntp"]
    recommended_apps = ["ope-fog", "ope-canvas", "ope-canvas-rce",
        "ope-smc", "ope-clamav", "ope-canvas-mathman"]
    stable_apps = ["ope-kalite", "ope-codecombat", "ope-gcf"]
    beta_apps = ["ope-freecodecamp", "ope-jsbin", "ope-rachel",
        "ope-stackdump", "ope-wamap", "ope-wsl", "ope-router"]
    # If this app gets turned on, make sure the depends do too
    app_depends = {
        "ope-canvas": ["ope-canvas-rce", "ope-canvas-mathman"],    
    }

    def set_internet_mode(self, mode):
        if mode.lower() == 'online':
            SyncOPEApp.server_mode = 'online'
        else:
            SyncOPEApp.server_mode = 'offline'

    def load_current_settings(self):
        global MAIN_WINDOW

        # Make sure we have a key set
        self.ensure_key()

        # TEST
        # self.set_offline_pw("1234")
        # Logger.info("OFFLINE PW: " + self.get_offline_pw())
        # self.set_online_pw("5678")
        # Logger.info("ONLINE PW: " + self.get_online_pw())

    def ensure_key(self):
        # Ensure we have a key
        auth = self.config.getdefault("Server", "auth1", "")
        if auth == "":
            auth = str(uuid.uuid4()).replace('-', '')
            self.config.set("Server", "auth1", auth)
            self.config.write()

    def get_offline_pw(self):
        self.ensure_key()
        key = self.config.getdefault("Server", "auth1", "")
        pw = self.config.getdefault("Server", "auth2", "")
        if pw != "":
            try:
                e = Enc(key)
                pw = e.decrypt(pw)
            except:
                # Error decrypting password
                pw = "changemeDJ2$#"
                popup = Popup(title='Error Getting Offline Password',
                              content=Label(text='Unable to get offline password, try setting it again.'),
                              size_hint=(None, None), size=(400, 400))
        else:
            pw = "changeme"
        return pw

    def set_offline_pw(self, pw):
        self.ensure_key()
        key = self.config.getdefault("Server", "auth1", "")
        e = Enc(key)
        pw = e.encrypt(str(pw))
        self.config.set("Server", "auth2", pw)
        self.config.write()

    def get_online_pw(self):
        self.ensure_key()
        key = self.config.getdefault("Server", "auth1", "")
        pw = self.config.getdefault("Server", "auth3", "")
        if pw != "":
            try:
                e = Enc(key)
                pw = e.decrypt(pw)
            except:
                # Error decrypting password
                pw = "changemeDJ2$#"
                popup = Popup(title='Error Getting Online Password',
                              content=Label(text='Unable to get online password, try setting it again.'),
                              size_hint=(None, None), size=(400, 400))
        else:
            pw = "changeme"
        return pw

    def set_online_pw(self, pw):
        self.ensure_key()
        key = self.config.getdefault("Server", "auth1", "")
        e = Enc(key)
        pw = e.encrypt(str(pw))
        self.config.set("Server", "auth3", pw)
        self.config.write()

    def build(self):
        global MAIN_WINDOW, sm

        self.icon = 'logo_icon.png'
        self.title = "Open Prison Education"
        self.settings_cls = SettingsWithSidebar
        MAIN_WINDOW = MainWindow()

        # Make sure to load current settings
        self.load_current_settings()

        # Populate data
        self.populate()

        # Add screens for each window we can use
        #sm.add_widget(StartScreen(name="start"))
        sm.add_widget(Factory.StartScreen(name='start'))
        sm.add_widget(Factory.ReleaseNotesScreen(name="release_notes"))
        sm.add_widget(Factory.GettingStartedScreen(name="getting_started"))
        sm.add_widget(Factory.VerifySettingsScreen(name="verify_settings"))
        sm.add_widget(Factory.PickAppsScreen(name="pick_apps"))
        sm.add_widget(Factory.OnlineModeScreen(name="online_mode"))
        sm.add_widget(Factory.OfflineModeScreen(name="offline_mode"))
        sm.add_widget(Factory.LoginScreen(name="login_screen"))
        sm.add_widget(Factory.OnlineUpdateScreen(name="online_update"))
        sm.add_widget(Factory.OfflineUpdateScreen(name="offline_update"))
        sm.add_widget(Factory.ManageFogScreen(name="manage_fog"))
        sm.add_widget(Factory.FogDownloadScreen(name="fog_download"))
        sm.add_widget(Factory.FogUploadScreen(name="fog_upload"))
        sm.add_widget(Factory.FogImportScreen(name="fog_import"))
        sm.add_widget(Factory.FogExportScreen(name="fog_export"))
        sm.add_widget(Factory.UtilitiesScreen(name="utilities"))
        sm.add_widget(Factory.UpdateSyncBoxesScreen(name="update_sync_boxes"))
        sm.add_widget(Factory.AppStatusScreen(name='app_status'))

        sm.current = "start"

        # Download popup object - for use later
        self.www_dl_control = Factory.WWWDownloadPopup()

        return sm  # MAIN_WINDOW

    def build_config(self, config):
        # Default settings
        config.setdefaults("Server",
                           {})
        config.setdefaults("Online Settings",
                           {'server_ip': '127.0.0.1',
                            'server_user': 'root',
                            'server_folder': '/ope',
                            'domain': 'ed',
                            })
        config.setdefaults("Offline Settings",
                           {'server_ip': '127.0.0.1',
                            'server_user': 'root',
                            'server_folder': '/ope',
                            'domain': 'ed',
                            })

        # Settings for ECASAS DNS
        config.setdefaults("eCasas",
                           {'ecasasweb_host': 'ecasas.ed',
                            'ecasasweb_ip': '127.0.0.1',
                            'ecasasdb_host': 'ecasasdb.ed',
                            'ecasasdb_ip': '127.0.0.1'
                            })

        # Generate defaults for selected apps
        selected_apps = {}
        # required apps
        for item in SyncOPEApp.required_apps:
            selected_apps[item] = '1'
        # recommended apps
        for item in SyncOPEApp.recommended_apps:
            selected_apps[item] = '1'
        # stable apps
        for item in SyncOPEApp.stable_apps:
            selected_apps[item] = '0'
        # beta apps #11 fixed
        for item in SyncOPEApp.beta_apps:
            selected_apps[item] = '0'

        config.setdefaults("Selected Apps",
                           selected_apps)

        # config.setdefaults("Build Settings",
        #                    {'build_folder': '~',
        #                     })
        # config.setdefaults("Transfer Settings", {})
        #
        # config.setdefaults("Development Settings", {})
        #
        # config.setdefaults("Production Settings", {})

    def build_settings(self, settings):
        # Register custom settings type
        settings.register_type('password', SettingPassword)
        settings.register_type('button', SettingButton)

        cwd = get_app_folder()
        settings.add_json_panel('Online Settings', self.config,
                                os.path.join(cwd, 'OnlineServerSettings.json'))
        settings.add_json_panel('Offline Settings', self.config,
                                os.path.join(cwd, 'OfflineServerSettings.json'))
        settings.add_json_panel('eCasas', self.config,
                                os.path.join(cwd, 'eCasas.json'))

        # Don't show this in settings AND in selected apps screen
        # settings.add_json_panel('Selected Apps', self.config, 'SelectedApps.json')

        # settings.add_json_panel('Source Settings', self.config, 'BuildSettings.json')
        # settings.add_json_panel('Transfer Settings', self.config, 'TransferSettings.json')
        # settings.add_json_panel('Development Settings', self.config, 'DevelopmentSettings.json')
        # settings.add_json_panel('Production Settings', self.config, 'ProductionSettings.json')

    def on_config_change(self, config, section, key, value):
        Logger.info("App.on_config_change: {0}, {1}, {2}, {3}".format(config, section, key, value))

        # If this is the password, save it
        if section == "Online Settings" and key == "server_password" and value == "btn_set_password":
            Logger.info("Saving online pw" + value)
            p = PasswordPopup()
            p.pw_func = self.set_online_pw
            p.open()
        if section == "Offline Settings" and key == "server_password" and value == "btn_set_password":
            Logger.info("Saving offline pw" + value)
            p = PasswordPopup()
            p.pw_func = self.set_offline_pw
            p.open()

        # Make sure the settings are stored in global variables
        self.load_current_settings()

    def close_settings(self, settings=None):
        # Settings panel closed
        Logger.info("App.close_settings: {0}".format(settings))
        super(SyncOPEApp, self).close_settings(settings)

    def log_message(self, msg):
        global MAIN_WINDOW

        # Log message to the log area on screen
        MAIN_WINDOW.ids.log_console.text += "\n" + msg
        # Scroll to the bottom
        MAIN_WINDOW.ids.log_console.scroll_y = 0

    def click_entry(self, item_id):
        Logger.info("App.click_entry {0}".format(item_id))

    def populate(self):
        global MAIN_WINDOW
        # Refresh data from database

    def pick_apps(self):
        # Show the screen to select apps to choose
        Logger.info("App.click_pick_apps")
        pass

    def get_file(self, fname):
        # Load the specified file
        ret = ""
        try:
            f = open(fname, "r")
            ret = f.read()
            f.close()
        except:
            # On failure just return ""
            pass
        # Convert git markdown to bbcode tags
        ret = markdown_to_bbcode(ret)
        return ret

    def copy_callback(self, transferred, total):
        global progress_widget
        # print("call back....")
        if progress_widget is None:
            # print("no progress widget set")
            return
        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        if total == 0:
            progress_widget.value = 0
        else:
            val = int(float(transferred) / float(total) * 100)
            if val < 0:
                val = 0
            if val > 100:
                val = 100
            if val != progress_widget.value:
                progress_widget.value = val

    def sftp_pull_files(self, remote_path, local_path, sftp, status_label, depth=1, filename=""):
        global progress_widget_label, APP_RUNNING
        if progress_widget_label is None:
            progress_widget_label = Label()

        # Adjust remote path if it is a file
        list_path = remote_path
        items = []
        if filename != "":
            list_path = os.path.join(remote_path, filename).replace("\\", "/")
            s = sftp.stat(list_path)
            s.filename = filename  # Make sure to add extra attrib filename so it matches what listdir_attr returns
            items.append(s)
        else:
            items = sftp.listdir_attr(list_path)

        # Recursive Walk through the folder and pull changed files
        depth_str = " " * depth
        # TODO - follow symlinks for folders/files
        for f in items:  # sftp.listdir_attr(list_path):
            if APP_RUNNING is not True:
                print("Exiting Early...")
                return
            if stat.S_ISDIR(f.st_mode):
                # status_label.text += "\n" + depth_str + "Found Dir: " + f.filename
                n_remote_path = os.path.join(remote_path, f.filename).replace("\\", "/")
                n_local_path = os.path.join(local_path, f.filename)
                self.sftp_pull_files(n_remote_path, n_local_path, sftp, status_label, depth+1)
            elif stat.S_ISREG(f.st_mode):
                # status_label.text += "\n" + depth_str + "Found File: " + remote_path  # f.filename
                # Try to copy it to the local folder
                try:
                    # Make sure the local folder exists
                    os.makedirs(local_path)
                except:
                    # Error if it exits, ignore
                    pass

                r_file = os.path.join(remote_path, f.filename).replace("\\", "/")
                l_file = os.path.join(local_path, f.filename)

                # Get the local modified time of the file
                l_mtime = 0
                try:
                    l_stat = os.stat(l_file)
                    l_mtime = int(l_stat.st_mtime)
                except:
                    # If there is an error, go with a 0 for local mtime
                    pass
                if f.st_mtime == l_mtime:
                    # status_label.text += "\n" + depth_str + "Files the same - skipping: " + f.filename
                    # progress_widget_label.text = f.filename + " (skip) "
                    pass
                elif f.st_mtime > l_mtime:
                    # status_label.text += "\n" + depth_str + "Remote file newer, downloading: " + f.filename
                    self.log_text_to_label(progress_widget_label, f.filename + " (dl) ")
                    sftp.get(r_file, l_file, callback=self.copy_callback)
                    os.utime(l_file, (f.st_mtime, f.st_mtime))
                else:
                    self.log_text_to_label(progress_widget_label, f.filename + " (newer, skip) ")
                    # status_label.text += "\n" + depth_str + "local file newer, skipping: " + f.filename

            else:
                # Non regular file
                self.log_text_to_label(progress_widget_label, f.filename + " (no reg file - skip)")

    def sftp_push_files(self, remote_path, local_path, sftp, status_label, depth=1, filename=""):
        global progress_widget_label, APP_RUNNING
        if progress_widget_label is None:
            progress_widget_label = Label()
        # Recursive Walk through the folder and push changed files
        depth_str = " " * depth

        # Need to decode unicode/mbcs encoded paths
        enc_local_path = os.fsdecode(local_path)  #.decode(sys.getfilesystemencoding())

        items = []
        if filename != "":
            items.append(filename)
        else:
            items = os.listdir(local_path)

        for item in items:  # os.listdir(local_path):
            if APP_RUNNING is not True:
                print("Exiting Early...")
                return
            enc_item = item
            try:
                enc_item = os.fsdecode(item) # item.decode(sys.getfilesystemencoding())
            except:
                # Set it first, then try to decode it, if decode fails use it as is
                pass
            l_path = os.path.join(enc_local_path, enc_item)
            if os.path.isdir(l_path):
                # status_label.text += "\n" + depth_str + "Found Dir: " + enc_item.encode('ascii', 'ignore')
                n_remote_path = os.path.join(remote_path, enc_item).replace("\\", "/")
                n_local_path = os.path.join(enc_local_path, enc_item)
                # Make sure the directory exists on the remote system
                sftp.chdir(remote_path)
                try:
                    sftp.mkdir(enc_item)
                except:
                    # Will fail if directory already exists
                    pass
                self.sftp_push_files(n_remote_path, n_local_path, sftp, status_label, depth+1)
            elif os.path.isfile(l_path):
                # status_label.text += "\n" + depth_str + "Found File: " + enc_item.encode('ascii', 'ignore')
                # Try to copy it to the remote folder

                r_file = os.path.join(remote_path, enc_item).replace("\\", "/")
                l_file = os.path.join(enc_local_path, enc_item)

                # Get the local modified time of the file
                l_mtime = 0
                try:
                    l_stat = os.stat(l_file)
                    l_mtime = int(l_stat.st_mtime)
                except:
                    # If there is an error, go with a 0 for local mtime
                    pass
                r_mtime = -1
                try:
                    # Get the stats for the remote file
                    stats = sftp.stat(r_file)
                    r_mtime = stats.st_mtime
                except:
                    pass
                if r_mtime == l_mtime:
                    # progress_widget_label.text = enc_item.encode('ascii', 'ignore') + " (skip) "
                    # status_label.text += " - Files the same - skipping. "
                    pass
                elif l_mtime > r_mtime:
                    self.log_text_to_label(progress_widget_label, enc_item + " (uploading) ")
                    # status_label.text += " - Local file newer, uploading..."
                    print("sftp_push_file - Local file newer, uploading " + l_file + " -> " + r_file + "...")
                    sftp.put(l_file, r_file, callback=self.copy_callback)
                    sftp.utime(r_file, (l_mtime, l_mtime))
                else:
                    self.log_text_to_label(progress_widget_label, enc_item + " (remote newer - skip) ")
                    # status_label.text += " - Remote file newer, skipping. "

            else:
                # Non regular file
                # progress_widget_label.text = enc_item.encode('ascii', 'ignore') + " (non reg file - skip)"
                pass

    def get_fog_image_list(self, initial=False):
        return FogDownloadFileSystem(self, initial)

    def get_fog_export_image_list(self):
        ssh_server = ""
        ssh_user = ""
        ssh_pass = ""
        ssh_folder = ""

        if SyncOPEApp.server_mode == 'online':
            ssh_server = self.config.getdefault("Online Settings", "server_ip", "127.0.0.1")
            ssh_user = self.config.getdefault("Online Settings", "server_user", "root")
            ssh_pass = self.get_online_pw()  # self.config.getdefault("Online Settings", "server_password", "changeme")
            ssh_folder = self.config.getdefault("Online Settings", "server_folder", "/ope")
        else:
            ssh_server = self.config.getdefault("Offline Settings", "server_ip", "127.0.0.1")
            ssh_user = self.config.getdefault("Offline Settings", "server_user", "root")
            ssh_pass = self.get_offline_pw()  # self.config.getdefault("Offline Settings", "server_password", "changeme")
            ssh_folder = self.config.getdefault("Offline Settings", "server_folder", "/ope")

        return FogSFTPFileSystem(ssh_server, ssh_user, ssh_pass, ssh_folder)

    def get_empty_fog_export_image_list(self):
        # Send back an empty SFTP file system
        return FogSFTPFileSystem()

    def toggle_server_mode(self, fog_export_server_mode, fog_export_to_usb_image):
        if fog_export_server_mode.active:
            SyncOPEApp.server_mode = 'online'
        else:
            SyncOPEApp.server_mode = 'offline'

        if fog_export_to_usb_image is not None:
            # fog_export_to_usb_image.file_system.pullimagelist()
            fog_export_to_usb_image.file_system = self.get_fog_export_image_list()
            fog_export_to_usb_image._update_files()

        return

    def start_fog_import_from_usb(self, fog_import_from_usb_image,
                                  fog_import_from_usb_button, fog_image_import_progress,
                                  error_message):
        error_message.text = ""
        # Verify import settings
        if (not fog_import_from_usb_image.selection or not fog_import_from_usb_image.selection[0] or
                'no images available' in fog_import_from_usb_image.selection[0]):
            error_message.text = "[b][color=ff0000]Please choose a valid image to import.[/color][/b]"
            return

        fog_import_from_usb_button.disabled = True

        threading.Thread(target=self.fog_import_from_usb_thread, args=(fog_import_from_usb_image,
                            fog_import_from_usb_button, fog_image_import_progress,
                            error_message)).start()

    def fog_import_from_usb_thread(self, fog_import_from_usb_image,
                                    fog_import_from_usb_button, fog_image_import_progress,
                                    error_message):
        fog_image_import_progress.value = 0

        # Connect to the server
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection()

        if ssh is None:
            error_message.text = err_str
            fog_import_from_usb_button.disabled = False
            return

        image_name = os.path.basename(fog_import_from_usb_image.selection[0]).strip("/")
        # Comes in with c:\\test....
        image_basename = image_name.replace(".fog_image", "")
        remote_path = os.path.join(ssh_folder, "volumes/fog/images/", image_basename).replace("\\", "/")
        remote_info_file = os.path.join(remote_path, image_basename + ".info").replace("\\", "/")
        remote_images_folder = os.path.join(ssh_folder, "volumes/fog/images/").replace("\\", "/")
        remote_tar_file = os.path.join(remote_images_folder, image_name).replace("\\", "/")
        local_file_path = os.path.join(self.get_fog_images_folder(), image_name)

        error_message.text = "Uploading " + image_basename + "."

        total_size = os.path.getsize(local_file_path)
        current_pos = 0
        last_update = time.time()
        dots = "."

        # open local file
        local_f = open(local_file_path, 'rb')
        # Push file to server
        sftp = ssh.open_sftp()

        start_time = time.time()
        end_time = 0

        with sftp.file(remote_tar_file, mode="wb", bufsize=8192) as remote_f:
            remote_f.set_pipelined()
            while True:
                data = local_f.read(8192)
                if not data:
                    break
                remote_f.write(data)
                current_pos += len(data)
                fog_image_import_progress.value = int(float(current_pos) / float(total_size) * 100)
                if time.time() - last_update > 1:
                    dots += "."
                    if len(dots) > 5:
                        dots = "."
                    upload_speed = ""
                    elapsed_time = time.time() - start_time
                    if elapsed_time == 0:
                        elapsed_time = 1
                    transfer_speed = float(current_pos / elapsed_time)
                    if transfer_speed == 0:
                        transfer_speed = 1
                    if int(elapsed_time) != 0:
                        upload_speed = get_human_file_size(transfer_speed) + "/s"
                    still_queued = total_size - current_pos
                    time_left = str(timedelta(seconds=int(still_queued / transfer_speed)))

                    error_message.text = "Uploading " + image_basename + "    " + upload_speed + "  " + time_left + dots
                    last_update = time.time()

        fog_image_import_progress.value = 100
        sftp.close()
        local_f.close()

        # Need to untar file
        error_message.text = "Unzipping " + image_name + " (will take several minutes)."
        # start a clock so it can show the dots and not look frozen
        progress_clock = Clock.schedule_interval(partial(self.fog_image_unzip_progress, error_message), 1.0)
        # Use ionice to limit io load during tar
        cmd = "cd " + remote_images_folder + "; ionice -c 3 -t tar xvf " + image_name + "; rm -Rf " + remote_tar_file + ";"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # causes it to read all lines
            print("> " + line)
            pass
        # Stop the progress clock
        progress_clock.cancel()

        # Clear current record for this image
        cmd = """docker exec -it ope-fog mysql -e "DELETE FROM fog.images WHERE imageName='""" + image_basename + """' LIMIT 1;" """
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # causes it to read all lines
            print("> " + line)
            pass

        # Copy the info file into the /var/lib/mysql-files so we can import it
        cmd = """docker exec -it ope-fog /bin/bash -c "rm /var/lib/mysql-files/""" + image_basename + """.info; cp /images/""" + image_basename + "/" + image_basename + """.info /var/lib/mysql-files/""" + image_basename + """.info; " """
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # causes it to read all lines
            print("> " + line)
            pass

        # Import database info from .info file
        cmd = """docker exec -it ope-fog mysql -e "LOAD DATA INFILE  '/var/lib/mysql-files/""" + image_basename + """.info'  INTO TABLE fog.images FIELDS TERMINATED BY ',' ENCLOSED BY '\\"' LINES TERMINATED BY '\\n' (imageName, imageDesc, imagePath, imageProtect, imageMagnetUri, imageDateTime, imageCreateBy, imageBuilding, imageSize, imageTypeID, imagePartitionTypeID, imageOSID, imageFormat, imageLastDeploy, imageCompress, imageEnabled, imageReplicate, imageServerSize)" """
        # FROM fog.images WHERE imageName='""" + image_name + """' INTO OUTFILE '/var/lib/mysql-files/""" + image_name + """.info' FIELDS TERMINATED BY ',' ENCLOSED BY '\\"' LINES TERMINATED BY '\\n'";"""
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # causes it to read all lines
            print("> " + line)
            pass

        ssh.close()

        fog_import_from_usb_button.disabled = False
        fog_image_import_progress.value = 100
        error_message.text = "Done!"

        return

    def fog_image_unzip_progress(self, error_message, *largs):
        # Update the message with dots.
        if error_message.text.endswith("....."):
            error_message.text = error_message.text.strip(".")
        error_message.text += "."

    def start_fog_export_to_usb(self, fog_export_to_usb_image,
                                fog_export_to_usb_button, fog_image_export_progress,
                                error_message):
        error_message.text = ""
        # Verify export settings
        if (not fog_export_to_usb_image.selection or not fog_export_to_usb_image.selection[0] or
                'no images available' in fog_export_to_usb_image.selection[0]):
            error_message.text = "[b][color=ff0000]Please choose a valid image to export.[/color][/b]"
            return

        fog_export_to_usb_button.disabled = True

        threading.Thread(target=self.fog_export_to_usb_thread, args=(fog_export_to_usb_image,
                                fog_export_to_usb_button, fog_image_export_progress,
                                error_message)).start()

    def fog_export_to_usb_thread(self, fog_export_to_usb_image,
                                fog_export_to_usb_button, fog_image_export_progress,
                                error_message):

        fog_image_export_progress.value = 0

        # Connect to the server
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection()

        if ssh is None:
            error_message.text = err_str
            fog_export_to_usb_button.disabled = False
            return

        # print("Security Options: " + str(ssh.get_transport().get_security_options().ciphers))

        image_name = os.path.basename(fog_export_to_usb_image.selection[0]).strip("/")  # .replace("C:\\", "").strip("/")  # Comes in with c:\\test....
        # print("Image Name: " + image_name)
        remote_path = os.path.join(ssh_folder, "volumes/fog/images/", image_name).replace("\\", "/")
        remote_images_folder = os.path.join(ssh_folder, "volumes/fog/images/").replace("\\", "/")
        local_file_path = os.path.join(self.get_fog_images_folder(), image_name + ".fog_image")
        # print("Local File Path: " + local_file_path)
        # print("Remote_FilePath: " + remote_path)
        error_message.text = "Downloading " + image_name

        # -- DUMP database data into the image folder for later import
        # - remove old mysql file, dump data and copy it to the images folder
        cmd = """docker exec -it ope-fog /bin/bash -c "rm /var/lib/mysql-files/""" + image_name + """.info;" """
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # print(":: " + line)
            pass

        # Dump file to mysql-files location
        cmd = """docker exec -it ope-fog mysql -e "SELECT imageName, imageDesc, imagePath, imageProtect, imageMagnetUri, imageDateTime, imageCreateBy, imageBuilding, imageSize, imageTypeID, imagePartitionTypeID, imageOSID, imageFormat, imageLastDeploy, imageCompress, imageEnabled, imageReplicate, imageServerSize FROM fog.images WHERE imageName='""" + image_name + """' INTO OUTFILE '/var/lib/mysql-files/""" + image_name + """.info' FIELDS TERMINATED BY ',' ENCLOSED BY '\\"' LINES TERMINATED BY '\\n'";"""
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # causes it to read all lines
            print(": " + line)
            pass

        # Move dump file to image folder
        cmd = """docker exec -it ope-fog bash -c "cp /var/lib/mysql-files/""" + image_name + """.info /images/""" + image_name + """/; ";"""
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            # causes it to read all lines
            print(": " + line)
            pass

        # Pull the dir size for this image...
        total_size = 1
        current_pos = 0

        # Figure out approx size of directory so we can show progress
        cmd = "du -sb " + remote_path + " | awk '{print $1}'"
        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        for line in stdout:
            try:
                total_size = int(line.strip())
            except Exception as ex:
                print("Error getting image size: " + str(ex))
                total_size = 1

        # Shave a little off due to gzip - an image that is already gzipped will not shave off much
        if total_size > 1:
            # With GZip, transfer size should be larger, so cut it down a bit so progress bar looks more accurate
            total_size = int(total_size * 1.0)

        # Now tar/gzip the folder and send it to the USB drive
        # Use ionice to limit io load during tar
        cmd = "cd " + remote_images_folder + "; ionice -c 3 -t tar cvf - " + image_name + " 2> /dev/null | gzip -fqc "
        # ssh.get_transport().window_size = 2147483647
        chan = ssh.get_transport().open_session()  # window_size=64000, max_packet_size=8192)
        chan.settimeout(10800)

        chan.exec_command(cmd)
        f = open(local_file_path, 'wb')
        chan_f = chan.makefile()
        chan_f._set_mode(mode="rb", bufsize=32768)

        last_update = time.time()
        dots = "."
        start_time = time.time()

        for line in chan_f:
            f.write(line)
            current_pos += len(line)
            fog_image_export_progress.value = int(float(current_pos) / float(total_size) * 100)

            if time.time() - last_update > 1:
                    dots += "."
                    if len(dots) > 5:
                        dots = "."
                    upload_speed = ""
                    elapsed_time = time.time() - start_time
                    if elapsed_time == 0:
                        elapsed_time = 1
                    transfer_speed = float(current_pos / elapsed_time)
                    if transfer_speed == 0:
                        transfer_speed = 1
                    if int(elapsed_time) != 0:
                        upload_speed = get_human_file_size(transfer_speed) + "/s"
                    still_queued = total_size - current_pos
                    time_left = str(timedelta(seconds=int(still_queued / transfer_speed)))

                    error_message.text = "Downloading " + image_name + "    " + upload_speed + "  " + time_left + dots
                    last_update = time.time()

        chan_f.close()
        chan.close()
        f.close()
        ssh.close()

        fog_export_to_usb_button.disabled = False
        fog_image_export_progress.value = 100
        error_message.text = "Done!"

        pass

    def start_fog_image_download(self, fog_image_download_url, fog_image_download_file,
                                 fog_image_download_button, fog_image_download_progress,
                                 error_message):
        error_message.text = ""
        # Verify the upload settings
        if fog_image_download_url.text == "":
            error_message.text = "[b][color=ff0000]Please fill out all the fields.[/color][/b]"
            return

        selection = ""
        if not fog_image_download_file.selection or not fog_image_download_file.selection[0]:
            error_message.text = "[b][color=ff0000]Please choose an image to download.[/color][/b]"
            return
        else:
            # Got a selection, see if it is one of our status/error messages
            s = fog_image_download_file.selection[0].replace("C:\\", "")
            if 'no images available' in s or 'Press refresh to pull list when online' in s:
                # It is our message, return w no action
                return
            selection = fog_image_download_file.selection[0]

        fog_image_download_button.disabled = True

        threading.Thread(target=self.fog_image_download_thread, args=(fog_image_download_url, fog_image_download_file,
                            fog_image_download_button, fog_image_download_progress,
                            error_message)).start()

    def fog_image_download_thread(self, fog_image_download_url, fog_image_download_file,
                                    fog_image_download_button, fog_image_download_progress,
                                    error_message):

        fog_image_download_progress.value = 0
        dl_name = fog_image_download_file.selection[0].replace("C:\\", "")  # Comes in with c:\\test....
        full_url = fog_image_download_url.text + "/" + dl_name
        local_file = os.path.join(self.get_fog_images_folder(), dl_name)

        # Grab the file...
        start_time = time.time()
        r = requests.get(full_url, stream=True)
        total_size = 1
        try:
            total_size = int(r.headers.get('content-length'))
        except Exception as ex:
            pass
        if total_size is None or total_size == 0:
            total_size = 1
        current_pos = 0

        last_update = time.time()-3
        dots = "."
        start_time = time.time()

        with open(local_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep alive chunks
                    f.write(chunk)
                    current_pos += len(chunk)
                if total_size == 0:
                    fog_image_download_progress.value = 0
                else:
                    fog_image_download_progress.value = int(float(current_pos) / float(total_size) * 100)

                if time.time() - last_update > 1:
                    dots += "."
                    if len(dots) > 5:
                        dots = "."
                    upload_speed = ""
                    elapsed_time = time.time() - start_time
                    if elapsed_time == 0:
                        elapsed_time = 1
                    transfer_speed = float(current_pos / elapsed_time)
                    if transfer_speed == 0:
                        transfer_speed = 1
                    if int(elapsed_time) != 0:
                        upload_speed = get_human_file_size(transfer_speed) + "/s"
                    still_queued = total_size - current_pos
                    time_left = str(timedelta(seconds=int(still_queued / transfer_speed)))

                    error_message.text = "Downloading " + dl_name + "    " + upload_speed + "  " + time_left + dots
                    last_update = time.time()

        fog_image_download_button.disabled = False
        error_message.text = "Done!"

    def start_fog_image_upload(self, fog_image_upload_server, fog_image_upload_folder, fog_image_upload_username,
                               fog_image_upload_password, fog_image_upload_file, fog_image_upload_send_button,
                               fog_image_upload_progress, error_message):

        error_message.text = ""
        # Verify the upload settings
        if (fog_image_upload_server.text == "" or fog_image_upload_folder.text == "" or
                fog_image_upload_username.text == "" or fog_image_upload_password.text == ""):
            error_message.text = "[b][color=ff0000]Please fill out all the fields.[/color][/b]"
            return

        if not fog_image_upload_file.selection or not fog_image_upload_file.selection[0]:
            error_message.text = "[b][color=ff0000]Please choose an image to upload.[/color][/b]"
            return

        fog_image_upload_send_button.disabled = True

        threading.Thread(target=self.fog_image_upload_thread, args=(fog_image_upload_server, fog_image_upload_folder, fog_image_upload_username,
                               fog_image_upload_password, fog_image_upload_file, fog_image_upload_send_button,
                               fog_image_upload_progress, error_message)).start()

    def fog_image_upload_thread(self, fog_image_upload_server, fog_image_upload_folder, fog_image_upload_username,
                               fog_image_upload_password, fog_image_upload_file, fog_image_upload_send_button,
                               fog_image_upload_progress, error_message):

        # Connect to the server
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection(
            ssh_server=fog_image_upload_server.text,
            ssh_user=fog_image_upload_username.text,
            ssh_pass=fog_image_upload_password.text)
        
        if ssh is None:
            print("Fog Image Upload - Unable to connect to ssh - " + str(err_str))
            self.log_text_to_label(error_message, "[b]UPLOAD ERROR[/b]\n" + err_str)
            fog_image_upload_send_button.disabled = False
            return
        
        push_file_name = os.path.basename(fog_image_upload_file.selection[0])

        # Start SFTP session
        sftp = ssh.open_sftp()

        # Set the progress widget and start the upload
        error_message.text = "Uploading " + push_file_name
        global sftp_progress_widget
        global sftp_progress_message
        sftp_progress_widget = fog_image_upload_progress
        sftp_progress_message = error_message
        # sftp.put(fog_image_upload_file.selection[0],
        #         os.path.join(fog_image_upload_folder.text, push_file_name).replace("\\", "/"),
        #         callback=self.sftp_copy_progress_callback)

        total_size = os.path.getsize(fog_image_upload_file.selection[0])
        current_pos = 0
        last_update = time.time()
        dots = "."

        # open local file
        local_f = open(fog_image_upload_file.selection[0], 'rb')
        # Push file to server
        sftp = ssh.open_sftp()

        start_time = time.time()
        end_time = 0

        remote_file = os.path.join(fog_image_upload_folder.text, push_file_name).replace("\\", "/")
        print("Pushing image: " + str(fog_image_upload_file.selection[0]) + " -> " + remote_file)

        try:
            with sftp.file(remote_file, mode="wb", bufsize=8192) as remote_f:
                print("opened")
                remote_f.set_pipelined()
                while True:
                    data = local_f.read(8192)
                    if not data:
                        break
                    remote_f.write(data)
                    current_pos += len(data)
                    fog_image_upload_progress.value = int(float(current_pos) / float(total_size) * 100)
                    if time.time() - last_update > 1:
                        dots += "."
                        if len(dots) > 5:
                            dots = "."
                        upload_speed = ""
                        elapsed_time = time.time() - start_time
                        if elapsed_time == 0:
                            elapsed_time = 1
                        transfer_speed = float(current_pos / elapsed_time)
                        if transfer_speed == 0:
                            transfer_speed = 1
                        if int(elapsed_time) != 0:
                            upload_speed = get_human_file_size(transfer_speed) + "/s"
                        still_queued = total_size - current_pos
                        time_left = str(timedelta(seconds=int(still_queued / transfer_speed)))

                        error_message.text = "Uploading " + push_file_name + "    " + upload_speed + "  " + time_left + dots
                        last_update = time.time()
        except Exception as ex:
            print("Unknown exception while uploading fog image: " + str(ex))
            self.log_text_to_label(error_message, "[b]ERROR[/b] - " + str(ex))

        fog_image_upload_progress.value = 100
        sftp.close()
        local_f.close()

        error_message.text = "[b]Done![/b]"
        fog_image_upload_send_button.disabled = False

        # Cleanup ssh stuff
        sftp.close()
        ssh.close()

        return

    def get_fog_images_folder(self):
        # Find the folder for fog images
        root_path = os.path.dirname(get_app_folder())
        volumes_path = os.path.join(root_path, "volumes")
        fog_path = os.path.join(volumes_path, "fog")
        fog_images_path = os.path.join(fog_path, "images").replace("/", os.sep)
        # print("FOG IMAGES PATH: " + fog_images_path)
        # Make sure the path exists
        if not os.path.isdir(fog_images_path):
            os.makedirs(fog_images_path)

        return fog_images_path

    def sync_volume(self, volume, folder, ssh, ssh_folder, status_label, branch="master", sync_type="sync", filename=""):
        # Sync files on the server with the USB drive

        # Get project folder (parent folder)
        root_path = os.path.dirname(get_app_folder())
        volumes_path = os.path.join(root_path, "volumes")
        volume_path = os.path.join(volumes_path, volume)
        folder_path = os.path.join(volume_path, folder.replace("/", os.sep))
        local_file_path = os.path.join(folder_path, filename)

        # Figure the path for the git app
        git_path = os.path.join(root_path, "bin/bin/git.exe")

        # Ensure the folder exists on the USB drive
        try:
            os.makedirs(folder_path)
        except:
            # will error if folder already exists
            pass

        # Ensure the folder exists on the server
        remote_folder_path = os.path.join(ssh_folder, "volumes", volume, folder).replace("\\", "/")
        remote_file_path = os.path.join(remote_folder_path, filename).replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("mkdir -p " + remote_folder_path, get_pty=True)
        stdin.close()
        for line in stdout:
            self.log_text_to_label(status_label, line)
            # make sure to read all lines, even if we don't print them
            pass

        self.log_text_to_label(status_label, "\n[b]Syncing Volume: [/b]" + volume + "/" + folder)
        sftp = ssh.open_sftp()

        # Copy remote files to the USB drive
        if sync_type == "sync" or sync_type == "dl":
            # self.log_text_to_label(status_label, "\nDownloading new files...")
            self.sftp_pull_files(remote_folder_path, folder_path, sftp, status_label, filename=filename)

        if sync_type == "sync" or sync_type == "ul":
            # Walk the local folder and see if there are files that don't exist that should be copied
            # self.log_text_to_label(status_label, "\nUploading new files...")
            self.sftp_push_files(remote_folder_path, folder_path, sftp, status_label, filename=filename)

        sftp.close()
        global progress_widget_label
        if progress_widget_label is not None:
            self.log_text_to_label(progress_widget_label, "")

    def git_pull_local(self, status_label, branch="master"):
        global GIT_REPOS
        ret = ""

        repos = GIT_REPOS
        #repos['test_repo'] = "https://234github.com/operepo/test_repo"

        # Pull each repo into a repo sub folder
        root_path = os.path.dirname(get_app_folder())
        repo_path = os.path.join(root_path, "volumes/repos")
        git_path = os.path.join(root_path, "bin/bin/git.exe")

        # os.chdir(root_path)

        # Make sure the folder exists
        if not os.path.isdir(repo_path) is True:
            # Doesn't exist, create it
            os.makedirs(repo_path)

        for repo in repos:
            self.log_text_to_label(status_label, "Pulling " + repo + " (may take several minutes)...")
            print("Pulling " + repo)
            # Make sure the repo folder exists
            f_path = os.path.join(repo_path, repo) + ".git"
            if not os.path.isdir(f_path) is True:
                os.mkdir(f_path)
            # Make sure git init is run
            # os.chdir(f_path)

            print("-- Init")
            proc = subprocess.Popen(git_path + " init --bare", cwd=f_path, stdout=subprocess.PIPE)
            proc.wait()
            print("Return Code: " + str(proc.returncode))
            # ret += proc.stdout.read().decode('utf-8')

            # Make sure we have proper remote settings
            print("-- Remove Remote")
            proc = subprocess.Popen(git_path + " remote remove ope_origin", cwd=f_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            print("Return Code: " + str(proc.returncode))
            # ret += proc.stdout.read().decode('utf-8')
            print("-- Add Remote")
            proc = subprocess.Popen(git_path + " remote add ope_origin " + repos[repo], cwd=f_path, stdout=subprocess.PIPE)
            proc.wait()
            print("Return Code: " + str(proc.returncode))
            # ret += proc.stdout.read().decode('utf-8')

            # Set fetch settings to pull all heads
            # print("-- config...")
            # proc = subprocess.Popen(git_path + " config remote.origin.fetch 'refs/heads/*:refs/heads/*' ", cwd=f_path, stdout=subprocess.PIPE)
            # proc.wait()
            # ret += proc.stdout.read().decode('utf-8')

            # Make sure we have the current stuff from github
            # +refs/heads/*:refs/heads/*
            print("-- Fetch")
            cmd = git_path + " --bare fetch ope_origin " + branch + ":master"
            proc = subprocess.Popen(cmd, cwd=f_path, bufsize=1, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # out = proc.communicate()[0]
            # print ("--- " + out)
            # for line in proc.stdout.readline():
            fetch_txt = ""
            for line in proc.stdout:
                #print("--- " + str(line))
                fetch_txt += line
            for line in proc.stderr:
                fetch_txt += line
            proc.wait()
            print("Return Code: " + str(proc.returncode))
            if proc.returncode == 0:
                self.log_text_to_label(status_label, " [color=00ff00]SUCCESS[/color]\n")
            else:
                self.log_text_to_label(status_label, " [color=ff0000]FAILED[/color] - " + str(proc.returncode) + "\n")
                self.log_text_to_label(status_label, "[color=ff3333]" + fetch_txt + "[/color]\n")

            #    status_label.text += line.decode('utf-8')
            #    Logger.info(line.decode('utf-8'))
            # ret += proc.stdout.read()

        #self.log_text_to_label(status_label, "\n[b]Done pulling repos[/b]")
        return ret

    def git_push_repo(self, ssh, ssh_server, ssh_user, ssh_pass, ssh_folder, status_label, online=True, branch="master", ):
        global GIT_REPOS
        ret = ""

        repos = GIT_REPOS

        remote_name = "ope_online"
        if online is not True:
            remote_name = "ope_offline"

        # Pull each repo into a repo sub folder
        root_path = os.path.dirname(get_app_folder())
        repo_path = os.path.join(root_path, "volumes/repos")
        git_path = os.path.join(root_path, "bin/bin/git.exe")

        # os.chdir(root_path)

        # Make sure the folder exists
        if not os.path.isdir(repo_path) is True:
            # Doesn't exist, create it
            os.makedirs(repo_path)

        # Ensure the base folder exists (e.g. /ope) and is ready for git commands
        stdin, stdout, stderr = ssh.exec_command("mkdir -p " + ssh_folder + "; cd " + ssh_folder + "; git init;", get_pty=True)
        stdin.close()
        for line in stdout:
            # status_label.text += line
            pass
        exit_status = stdout.channel.recv_exit_status()
        print("Return Code: " + str(exit_status))

        for repo in repos:
            self.log_text_to_label(status_label, "Pushing " + repo + " (may take several minutes)... ")
            print("Pushing " + repo)
            # Make sure the repo folder exists
            f_path = os.path.join(repo_path, repo) + ".git"
            if not os.path.isdir(f_path) is True:
                os.mkdir(f_path)

            # os.chdir(f_path)

            # Ensure the folder exists, is a repo, and has a sub folder (volumes/smc/???.git) that is a bare repo
            remote_repo_folder = os.path.join(ssh_folder, "volumes/smc/git/" + repo + ".git").replace("\\", "/")
            remote_repo_folder_path = remote_repo_folder
            if remote_repo_folder_path.startswith("~"):
                # Make sure we use a / in the beginning so it doesn't mess stuff up
                remote_repo_folder_path = "/" + remote_repo_folder_path
            ret += "\n\n[b]Ensuring git repo " + repo + " setup properly...[/b]\n"
            print("-- Init")
            stdin, stdout, stderr = ssh.exec_command("mkdir -p " + remote_repo_folder + "; cd " + remote_repo_folder + "; git init --bare; ", get_pty=True)
            stdin.close()
            for line in stdout:
                # status_label.text += line
                # make sure to read all lines, even if we don't print them
                pass
            exit_status = stdout.channel.recv_exit_status()
            print("Return Code: " + str(exit_status))

            # Remove existing remote - in case it is old/wrong
            print("-- Remove Remote")
            proc = subprocess.Popen(git_path + " remote remove " + repo + "_" + remote_name, cwd=f_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            # for line in proc.stdout:
            #    status_label.text += line
            exit_status = proc.returncode
            print("Return Code: " + str(exit_status))

            # Add current remote address
            print("-- Add Remote")
            proc = subprocess.Popen(git_path + " remote add " + repo + "_" + remote_name + " ssh://" + ssh_user + "@" + ssh_server + ":" + remote_repo_folder_path, cwd=f_path, stdout=subprocess.PIPE)
            proc.wait()
            # for line in proc.stdout:
            #    status_label.text += line
            exit_status = proc.returncode
            print("Return Code: " + str(exit_status))

            # Push to the remote server
            print("-- Push")
            proc = subprocess.Popen(git_path + " push " + repo + "_" + remote_name + " " + branch,
                cwd=f_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
            push_text = ""
            for line in proc.stdout:
               push_text += line
               #Logger.info(line)
            for line in proc.stderr:
                push_text += line.decode()
            exit_status = proc.returncode
            print("Return Code: " + str(exit_status))
            if exit_status == 0:
                self.log_text_to_label(status_label, "[color=00ff00]SUCCESS[/color]\n")
            else:
                self.log_text_to_label(status_label, "[color=ff0000]FAILED[/color] - " + str(exit_status))
                self.log_text_to_label(status_label, "\n[color=ff0000]" + push_text + "[/color]\n")

        # Repos are in place, now make sure to checkout the main ope project in the
        # folder on the server (e.g. cd /ope; git pull local_bare origin)

        # Ensure that local changes are stash/saved so that the pull works later
        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git stash;", get_pty=True)
        stdin.close()
        for line in stdout:
            # status_label.text += line
            # make sure to read all lines, even if we don't print them
            pass

        # Have remote server checkout from the bare repo
        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git remote remove local_bare;", get_pty=True)
        stdin.close()
        for line in stdout:
            # status_label.text += line
            # Logger.info(line)
            # make sure to read all lines, even if we don't print them
            pass

        ope_local_bare = os.path.join(ssh_folder, "volumes/smc/git/ope.git").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git remote add local_bare " + ope_local_bare + ";", get_pty=True)
        stdin.close()
        for line in stdout:
            # status_label.text += line
            # Logger.info(line)
            # make sure to read all lines, even if we don't print them
            pass

        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git pull local_bare " + branch + ";", get_pty=True)
        stdin.close()
        for line in stdout:
            print("---- " + line)
        #   # status_label.text += line
        #    Logger.info(line)
            # Make sure to read stdout and let this process finish
            pass

        #self.log_text_to_label(status_label, "Done pulling repos to USB drive")
        return ret

    def get_enabled_apps(self):
        # Return a list of enabled apps

        # Start with required apps
        enabled_apps = SyncOPEApp.required_apps[:]

        # Check recommended apps
        for item in SyncOPEApp.recommended_apps:
            if self.config.getdefault("Selected Apps", item, "1") == "1":
                enabled_apps.append(item)

        # Check stable apps
        for item in SyncOPEApp.stable_apps:
            if self.config.getdefault("Selected Apps", item, "0") == "1":
                enabled_apps.append(item)
        # Check beta apps
        for item in SyncOPEApp.beta_apps:
            if self.config.getdefault("Selected Apps", item, "0") == "1":
                enabled_apps.append(item)

        return enabled_apps

    def enable_apps(self, ssh, ssh_folder, status_label):
        ret = ""
        # Get the list of enabled apps
        apps = self.get_enabled_apps()

        # Clear all the enabled files
        stdin, stdout, stderr = ssh.exec_command("rm -f " + ssh_folder + "/docker_build_files/ope-*/.enabled", get_pty=True)
        stdin.close()
        r = stdout.read()
        if len(r) > 0:
            self.log_text_to_label(status_label, "\n" + r.decode('utf-8'))

        for a in apps:
            self.log_text_to_label(status_label, "\n-- Enabling App: " + a)
            app_path = os.path.join(ssh_folder, "docker_build_files", a)
            enabled_file = os.path.join(app_path, ".enabled")
            enable_cmd = "mkdir -p " + app_path + "; touch " + enabled_file
            stdin, stdout, stderr = ssh.exec_command(enable_cmd.replace('\\', '/'), get_pty=True)
            stdin.close()
            r = stdout.read()
            if len(r) > 0:
                self.log_text_to_label(status_label, "\n" + r.decode('utf-8'))
        self.log_text_to_label(status_label, "....")
        return ret

    def write_ope_env_values(self, ssh, ssh_pass, build_path, ip, domain):
        # Write all ENV values for the OPE apps - used when rebuilding docker-compose.yml file

        # - Server IP
        #self.write_ope_env_value(ssh, build_path, "ip", ip)
        self.write_ope_env_value(ssh, build_path, "IP", ip)  # use caps for new builds
        # - Server Domain (e.g. .ed)
        #self.write_ope_env_value(ssh, build_path, "domain", domain)
        self.write_ope_env_value(ssh, build_path, "DOMAIN", domain)  # use caps for new builds
        # - Psss apps will use as the admin/root pw
        #self.write_ope_env_value(ssh, build_path, "pw", ssh_pass)
        self.write_ope_env_value(ssh, build_path, "IT_PW", ssh_pass)
        self.write_ope_env_value(ssh, build_path, "OFFICE_PW", ssh_pass)
        self.write_ope_env_value(ssh, build_path, "TEST_PW", "$3@hawks!2")
        # - Running in online or offline mode
        self.write_ope_env_value(ssh, build_path, "IS_ONLINE", self.is_online())
        # - Extra settings for domain resolution
        dns_extras = ""
        # -- Add A entries for ecasas
        dns_extras += " -A /" + self.config.getdefault("eCasas", "ecasasweb_host", "ecasas.ed") + \
                      "/" + self.config.getdefault("eCasas", "ecasasweb_ip", "127.0.0.1") + \
                      " -A /" + self.config.getdefault("eCasas", "ecasasdb_host", "ecasasdb.ed") + \
                      "/" + self.config.getdefault("eCasas", "ecasasdb_ip", "127.0.0.1")
        self.write_ope_env_value(ssh, build_path, "DNS_EXTRAS", dns_extras)

    def write_ope_env_value(self, ssh, path, key, value):
        ret = True
        #print("Writing " + key)
        try:
            f_name = "." + str(key).upper()  # Don't do upper as file name case matters
            ssh_cmd = "cd " + str(path) + "; echo \"" + ssh_utils.quote_argument(str(value)) + "\" > " + f_name + "; "
            #print("running: " + ssh_cmd)
            stdin, stdout, stderr = ssh.exec_command( ssh_cmd, get_pty=True)
            for line in stdout:
                print(line)
                pass
        except Exception as ex:
            ret = False
            err_msg = "Error writing ENV value " + str(key) + "  ---> " + str(ex)
            Logger.info(err_msg)
            print(err_msg)

        return ret

    def pull_docker_images(self, ssh, ssh_folder,  status_label, ip, domain, ssh_pass):
        # Run on the online server - pull the current docker images
        ret = ""

        # Figure out where we are dumping our ENV values
        build_path = os.path.join(ssh_folder, "docker_build_files").replace("\\", "/")

        # Save out our ENV values to the server so we can use them when running
        self.write_ope_env_values(ssh, ssh_pass, build_path, ip, domain)

        # Need to re-run the rebuild_compose.py file to build the docker-compose.yml file
        rebuild_path = os.path.join(ssh_folder, "build_tools", "rebuild_compose.py").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("python " + rebuild_path + " auto", get_pty=True)
        try:
            # Write a couple enters in case this is the first time the script is run
            stdin.write("\n\n")
        except:
            pass
        stdin.close()
        for line in stdout:
            self.log_text_to_label(status_label, line)
            pass

        # Run the pull command
        self.log_text_to_label(status_label, "\n[b]Pulling docker apps...[/b]\n")
        docker_files_path = os.path.join(ssh_folder, "docker_build_files").replace("\\", "/")
        pull_failed = False
        for app in self.get_enabled_apps():
            self.log_text_to_label(status_label, "- Pulling " + app + "... ")
            stdin, stdout, stderr = ssh.exec_command("cd " + docker_files_path + "; docker-compose pull " + app + ";", get_pty=True)
            stdin.close()
            for line in stdout:
                # self.log_text_to_label(status_label, line)
                # Logger.info(line)
                pass
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                self.log_text_to_label(status_label, " [color=00ff00] SUCCESS [/color] \n")
            else:
                self.log_text_to_label(status_label, " [color=ff0000] FAILED TO PULL - This failure may prevent other apps from coming online[/color]\n[color=ff0000] -- please fix the issue or disable this app and re-run the sync process. [/color] \n")
                print("**** ERROR - Failed to pull " + str(app) + " from hub.docker.com " + str(exit_status))
                pull_failed = True

        if pull_failed:
            self.log_text_to_label(status_label, "[color=ff0000] WARNING - Some OPE Apps (Docker Images) failed to pull![/color]\n")
        return ret

    def save_docker_images(self, ssh, ssh_folder, status_label):
        # Dump docker images to the app_images folder on the server
        ret = ""

        # Run the script that is on the server
        save_script = os.path.join(ssh_folder, "sync_tools", "export_docker_images.py").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("python " + save_script, get_pty=True)
        stdin.close()
        for line in stdout:
            self.log_text_to_label(status_label, line)

        return ret

    def load_docker_images(self, ssh, ssh_folder, status_label):
        # Import docker images from the app_images folder on the server
        ret = ""

        load_script = os.path.join(ssh_folder, "sync_tools", "import_docker_images.py").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("python " + load_script, get_pty=True)
        stdin.close()
        for line in stdout:
            # self.log_text_to_label(status_label, line.decode('utf-8'))
            # self.log_text_to_label(status_label, ".")
            pass

        return ret

    def start_apps(self, ssh, ssh_folder, ssh_pass, status_label, ip, domain):
        # Start the docker apps by calling the up.sh script
        ret = ""

        build_path = os.path.join(ssh_folder, "docker_build_files").replace("\\", "/")

        # Save out our ENV values to the server so we can use them when running
        self.write_ope_env_values(ssh, ssh_pass, build_path, ip, domain)

        # Run twice - sometimes compose fails, so we just rerun it
        # Add auto param to up.sh - to prevent it from asking questions
        stdin, stdout, stderr = ssh.exec_command("cd " + build_path + "; sh up.sh auto; sleep 5; sh up.sh ", get_pty=True)
        stdin.close()
        for line in stdout.read():
            # self.log_text_to_label(status_label, str(line))
            # print("- " + str(line), end='')
            pass

        return ret

    def copy_docker_images_to_usb_drive(self, ssh, ssh_folder, status_label, progress_bar):
        global progress_widget

        progress_widget = progress_bar

        # Copy images from online server to usb drive
        ret = ""

        # Ensure the local app_images folder exists
        try:
            os.makedirs(os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images"))
        except:
            # Throws an error if already exists
            pass

        # Use the list of enabled images
        apps = self.get_enabled_apps()

        sftp = ssh.open_sftp()

        # Check each app to see if we need to copy it
        for app in apps:
            self.set_progress_value(progress_bar, 0)
            # Download the server digest file
            online_digest = "."
            current_digest = "..."
            remote_digest_file = os.path.join(ssh_folder, "volumes", "app_images", app + ".digest").replace("\\", "/")
            local_digest_file = os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images", app + ".digest.online")
            current_digest_file = os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images", app + ".digest")
            remote_image = os.path.join(ssh_folder, "volumes", "app_images", app + ".tar.gz").replace("\\", "/")
            local_image = os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images", app + ".tar.gz")
            # print("Getting File: " + str(remote_digest_file) + "->" + str(local_digest_file))
            sftp.get(remote_digest_file, local_digest_file)

            # Read the online digest info
            try:
                f = open(local_digest_file, "r")
                online_digest = f.read().strip()
                f.close()
            except:
                # Unable to read the local digest, just pass
                pass

            # Read the current digest info
            try:
                f = open(current_digest_file, "r")
                current_digest = f.read().strip()
                f.close()
            except:
                # Unable to read the local digest, just pass
                pass

            # If digest files don't match, copy the file to the local folder
            if online_digest != current_digest or not os.path.exists(local_image):
                self.log_text_to_label(status_label, "\nCopying App: " + app)
                sftp.get(remote_image, local_image, callback=self.copy_docker_images_to_usb_drive_progress_callback)
                # Logger.info("Moving on...")
                # Store the current digest
                try:
                    f = open(current_digest_file, "w")
                    f.write(online_digest)
                    f.close()
                except:
                    self.log_text_to_label(status_label, "Error saving current digest: " + current_digest_file)
            else:
                self.log_text_to_label(status_label, "\nApp hasn't changed, skipping: " + app)
            #

        sftp.close()
        return ret

    def sftp_copy_progress_callback(self, transferred, total):
        global sftp_progress_widget
        global sftp_progress_message
        global sftp_progress_last_update

        if sftp_progress_widget  is None:
            return

        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        if total == 0:
            self.set_progress_value(sftp_progress_widget, 0)
        else:
            self.set_progress_value(sftp_progress_widget, int(float(transferred) / float(total) * 100))

        if not sftp_progress_message is None and time.time() - sftp_progress_last_update > 1:
            self.log_text_to_label(sftp_progress_message, ".")
            txt = sftp_progress_message.text
            if txt.endswith("....."):
                self.log_text_to_label(sftp_progress_message, txt.strip("."), True)
            sftp_progress_last_update = time.time()

    def copy_docker_images_to_usb_drive_progress_callback(self, transferred, total):
        global progress_widget

        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        if total == 0:
            self.set_progress_value(progress_widget, 0)
        else:
            self.set_progress_value(progress_widget, int(float(transferred) / float(total) * 100))

    def copy_docker_images_from_usb_drive(self, ssh, ssh_folder, status_label, progress_bar):
        global progress_widget

        progress_widget = progress_bar

        # Copy images from usb drive to the offline server
        ret = ""

        # Ensure the local app_images folder exists
        try:
            os.makedirs(os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images"))
        except:
            # Throws an error if already exists
            pass

        # Ensure that server has app_images folder
        app_images_path = os.path.join(ssh_folder, "volumes", "app_images").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("mkdir -p " + app_images_path, get_pty=True)
        stdin.close()
        ret += stdout.read().decode('utf-8')

        # Use the list of enabled images
        apps = self.get_enabled_apps()

        sftp = ssh.open_sftp()

        # Check each app to see if we need to copy it
        for app in apps:
            # TODO - Copying every time?
            self.set_progress_value(progress_bar, 0)
            # Download the server digest file
            offline_digest = "."
            current_digest = "..."
            remote_digest_file = os.path.join(ssh_folder, "volumes", "app_images", app + ".digest").replace("\\", "/")
            local_digest_file = os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images", app + ".digest.offline")
            current_digest_file = os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images", app + ".digest")
            remote_image = os.path.join(ssh_folder, "volumes", "app_images", app + ".tar.gz").replace("\\", "/")
            local_image = os.path.join(os.path.dirname(get_app_folder()), "volumes", "app_images", app + ".tar.gz")

            # Make sure to remove the local digest file - keeps us from assuming it has been copied during edge cases
            if os.path.isfile(local_digest_file):
                os.unlink(local_digest_file)

            try:
                sftp.get(remote_digest_file, local_digest_file)
            except:
                # If we can't get this file, its ok, just assume we need to copy
                pass

            # Read the online digest info
            try:
                f = open(local_digest_file, "r")
                offline_digest = f.read().strip()
                f.close()
            except:
                # Unable to read the local digest, just pass
                pass

            # Read the current digest info
            try:
                f = open(current_digest_file, "r")
                current_digest = f.read().strip()
                f.close()
            except:
                # Unable to read the local digest, just pass
                pass

            # If digest files don't match, copy the file to the local folder
            if offline_digest != current_digest:
                self.log_text_to_label(status_label, "\nCopying App: " + app)
                try:
                    sftp.put(local_image, remote_image, callback=self.copy_docker_images_from_usb_drive_progress_callback)
                except:
                    self.log_text_to_label(status_label, "\n       [b][color=ff0000]Error[/color][/b] pushing " + local_image + \
                        "  -- make sure you have pulled it properly by running the Online Sync first.")
                    continue
                # Logger.info("Moving on...")
                # Store the current digest
                try:
                    f = open(local_digest_file, "w")
                    f.write(current_digest)
                    f.close()
                except:
                    self.log_text_to_label(status_label, "Error saving current digest: " + current_digest_file)
                # Copy digest file to server
                try:
                    sftp.put(local_digest_file, remote_digest_file)
                except:
                    self.log_text_to_label(status_label, "Error pushing digest file to server:  " + local_digest_file)
            else:
                self.log_text_to_label(status_label, "\nApp hasn't changed, skipping: " + app)
            #

        sftp.close()
        return ret

    def copy_docker_images_from_usb_drive_progress_callback(self, transferred, total):
        global progress_widget
        if progress_widget is None:
            return

        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        if total == 0:
            self.set_progress_value(progress_widget, 0)
        else:
            self.set_progress_value(progress_widget, int(float(transferred) / float(total) * 100))

    def sync_volumes(self, ssh, ssh_folder, status_label, online_state='online'):
        # Sync volumes of offline OR online server to USB drive
        # TODO - check enabled apps first

        apps = self.get_enabled_apps()
        for app in apps:
            if app == "ope-canvas":
                # Sync canvas files (student and curriculum files)
                # self.sync_volume('canvas', 'tmp/files', ssh, ssh_folder, status_label)
                # - sync canvas db (sync db dumps)
                # self.sync_volume('canvas', 'db/sync', ssh, ssh_folder, status_label)

                # TODO - rebuild canvas assets
                # docker exec -it ope-canvas bash -c "$GEM_HOME/bin/bundle exec rake canvas:compile_assets"
                pass
            
            if app == "ope-canvas-rce":
                # Remote content editor for canvas - shouldn't need to sync at all
                pass

            if app == "ope-smc":
                # Sync SMC movies
                # self.sync_volume('smc', 'media', ssh, ssh_folder, status_label)
                # TODO - trigger movie import
                pass

            if app == "ope-fog":
                # Sync FOG images
                # self.sync_volume('fog', 'share_images', ssh, ssh_folder, status_label)
                # TODO - trigger image import
                pass

            if app == "ope-postgresql":
                # Dump data so we can import/sync/merge it
                cmd = "docker-compose exec ope-postgresql bash -c 'mkdir -p /db_backup/canvas/canvas_production'"
                cmd = "docker-compose exec ope-postgresql bash -c 'pg_dump -d canvas_production -U postgres -f /db_backup/canvas/canvas_production -F d --data-only --blobs --disable-triggers --quote-all-identifiers'"

                # self.sync_volume('postgresql', 'canvas', ssh, ssh_folder, status_label)
                pass

            if app == "ope-gcf":
                self.log_text_to_label(status_label, "\n\n[b]Syncing GCF Volume[/b]")
                # Make sure we have the local zip file on the drive
                gcf_zip_filename = 'gcf.zip'
                # gcf_zip_filename = 'gcf.test.zip'

                # Calculate the web url
                gcf_url_path = SyncOPEApp.ope_resources_url + "/gcflearnfree/" + gcf_zip_filename

                # Calculate local file path
                root_path = os.path.dirname(get_app_folder())
                volumes_path = os.path.join(root_path, "volumes")
                volume_path = os.path.join(volumes_path, "gcf")
                folder_path = os.path.join(volume_path, "zip")
                gcf_zip_file_path = os.path.join(folder_path, gcf_zip_filename)
                # Make sure folders exist
                os.makedirs(folder_path, exist_ok=True)

                if online_state == "online":
                    # Start the download
                    self.log_text_to_label(status_label, "\n[b]Starting Download [/b] -  (about 9 gig) " + gcf_url_path)

                    dl_thread = self.start_www_download(gcf_url_path, gcf_zip_file_path)
                    ret = self.wait_for_www_download(dl_thread)
                    if ret == "Complete":
                        # Success!
                        self.log_text_to_label(status_label, "\n[b]Download Complete![/b]")
                    else:
                        # Error!
                        self.log_text_to_label(status_label, "\n[b]Download Error![/b]\n - " + ret)
                        
                sync_type = 'dl'
                if online_state == 'offline':
                    sync_type = 'ul'
                
                if os.path.exists(gcf_zip_file_path):
                    # Zip file exists on USB drive, make sure it exists on the server
                    # NOTE - ALWAYS upload this file to the OPE server
                    self.sync_volume('gcf', 'zip', ssh, ssh_folder, status_label,
                        sync_type='ul', filename=gcf_zip_filename)

                    self.log_text_to_label(status_label, "\nUnzipping GCF files (about 9 gig, may take 1-10 minutes)...\n")
                    
                    # Make sure the zip file has been unzipped to the gcf folder
                    ssh_command = "cd " + ssh_folder + "/volumes/gcf/zip; " + \
                        " if [ ! -f .unpacked ]; then unzip -qo " + gcf_zip_filename + " -d ../www/; touch .unpacked; else echo 'already unpacked'; fi;"
                    stdin, stdout, stderr = ssh.exec_command(ssh_command, get_pty=True)
                    stdin.close()
                    out = ""
                    for line in stdout:
                        # causes it to read all lines
                        out += line
                        pass
                    #out = stdout.read().decode('utf-8').strip()
                    #print(out)
                    pass

                self.log_text_to_label(status_label, "\n[b]Finished syncing GCF Volume[/b]\n\n")


            if app == "ope-kalite":
                sync_type = 'dl'
                if online_state == 'offline':
                     sync_type = 'ul'
                # Sync video files
                self.sync_volume('kalite', 'database', ssh, ssh_folder, status_label,
                                 sync_type=sync_type, filename='content_khan_en.sqlite')
                self.sync_volume('kalite', '', ssh, ssh_folder, status_label,
                                 sync_type=sync_type, filename='secretkey.txt')
                self.sync_volume('kalite', '', ssh, ssh_folder, status_label,
                                 sync_type=sync_type, filename='settings.py')
                self.sync_volume('kalite', 'content', ssh, ssh_folder, status_label, sync_type=sync_type)
                self.sync_volume('kalite', 'locale', ssh, ssh_folder, status_label, sync_type=sync_type)
                self.sync_volume('kalite', 'httpsrv', ssh, ssh_folder, status_label, sync_type=sync_type)


                # TODO - Do we need to sync other folders? locale?
            
            if app == "ope-codecombat":
                # open sftp connection and move to the codecombat data folder
                sftp = ssh.open_sftp()
                server_path = os.path.join(ssh_folder, "volumes/codecombat/data").replace("\\", "/")
                sftp.chdir(server_path)
                
                if online_state == "online":
                    # ONLINE
                    # Wait for .dl_complete file to show up, then download the dump.tar.gz file
                    # TODO - need if file exists?
                    dl_complete_found = False
                    while not dl_complete_found:
                        # Grab a list of files
                        f_list = sftp.listdir_attr(server_path)
                        for f_item in f_list:
                            if f_item.filename == ".dl_complete":
                                dl_complete_found = True
                        # waiting for database to download and unpack
                        print("waiting for db to dl...")
                        time.sleep(0.25)
                        # Thread.sleep(3)
                    
                    self.sync_volume('codecombat', 'data', ssh, ssh_folder, status_label, sync_type='dl', filename='dump.tar.gz')
                else:
                    # OFFLINE TODO
                    # Copy dump.tar.gz file
                    # unpack file 
                    # touch  .unpacked file to signal that db is ready for import
                    self.sync_volume('codecombat', 'data', ssh, ssh_folder, status_label, sync_type='ul', filename='dump.tar.gz')
                    ssh_command = "cd " + ssh_folder + "/volumes/codecombat/data; tar xzf dump.tar.gz; touch .unpacked;"
                    stdin, stdout, stderr = ssh.exec_command(ssh_command, get_pty=True)
                    stdin.close()
                    out = stdout.read().decode('utf-8').strip()
                
                sftp.close()

    def start_www_download(self, download_url, local_file_path):
        
        if self.www_dl_control is None:
            print("Error - self.www_dl_cotrol needs to be created prior to calling start_www_download!")
            return
            
        self.www_dl_in_progress = True
        self.www_dl_status = ""

        # Start the download thread to do the work
        t = threading.Thread(target=self.start_www_download_worker,
            args=(download_url, local_file_path, self.www_dl_control))
        
        t.start()
        
        return t

    def www_file_is_older(self, local_time, url_time):
        ret = True
        # Is the local file older then the web file?
        #print url_time  #emits 'Sat, 28 Mar 2015 08:05:42 GMT' on my machine
        #print file_time #emits '2015-03-27 21:53:28.175072' 

        # Parse the url time
        #parsed_url_time = datetime.datetime.strptime(url_time,
        #    '%a, %d %b %Y %X %Z')
        parsed_url_time = parsedate(url_time)
        
        return local_time < parsed_url_time, parsed_url_time

    @mainthread
    def log_text_to_label(self, label_control, text, clear_previous_text=False):
        # Do this in the main thread so that it doesn't mess with kivy
        try:
            if label_control is not None:
                if clear_previous_text is True:
                    label_control.text = text
                else:
                    label_control.text += text
            else:
                print("Skipping log - label_control is none!")
        except Exception as ex:
            print("Unknown Error (log_text_to_label) - " + str(ex))
            traceback.print_exc()

    @mainthread
    def set_progress_value(self, progress_control, value):
        # Set the value in the main thread so we don't get weird threading issues
        if progress_control is not None:
            progress_control.value = value
    
    @mainthread
    def set_button_disabled(self, button_control, value):
        # Set the value in the main thread so we don't get weird threading issues
        if button_control is not None:
            button_control.disabled = value

    @mainthread
    def open_www_dl_control(self):
        self.www_dl_control.open()
    
    @mainthread
    def dismiss_www_dl_control(self):
        self.www_dl_control.dismiss()

    def start_www_download_worker(self, download_url, local_file_path, download_popup):
        self.open_www_dl_control()

        self.log_text_to_label(self.www_dl_control.ids.www_dl_label, "Processing " + download_url + "...", True)
        print("Processing " + download_url + " -> " + local_file_path)

        try:
            need_to_dl = False
            current_pos = 0

            start_time = time.time()
            r = requests.get(download_url, stream=True)
            total_size = 1
            try:
                total_size = int(r.headers.get('content-length'))
            except:
                pass
            if total_size is None or total_size == 0:
                total_size = 1
            
            local_file_size = 0
            try:
                local_file_size = os.path.getsize(local_file_path)
            except:
                # It is ok if the file doesn't exist, just put it at 0 bytes
                local_file_size = 0
            
            if total_size != local_file_size:
                need_to_dl = True
                print("File sizes do not match, downloading " + download_url + "...")

            print("URL / Local file size: " + str(total_size) + " / " + str(local_file_size))

            # Get the modified date/time
            mod_date_time = time.time()
            try:
                mod_date_time = r.headers.get('last-modified')
            except:
                pass

            try:
                local_file_time = datetime.fromtimestamp(os.path.getmtime(local_file_path), 
                    tz=timezone.utc)
            except:
                # No local file, so set date to epoch time
                print("---> Local file doesn't exist")
                local_file_time = datetime.fromtimestamp(0,
                    tz=timezone.utc)

            is_older, url_time = self.www_file_is_older(local_file_time, mod_date_time)
            if is_older == True:
                print("local file is older or missing, need to dl")
                need_to_dl = True
            else:
                print("Local file is same date or newer")
            
            print("URL / Local file time: " + str(mod_date_time) + " / " + str(local_file_time))

            if need_to_dl is not True:
                # File size and time match, don't download
                print("File already present, skipping download.")
                self.log_text_to_label(self.www_dl_control.ids.www_dl_label, download_url + " already in cache, skipping.")
                self.www_dl_status = "Complete"
                # Done w the download, close the popup
                #self.www_dl_control.dismiss()
                self.dismiss_www_dl_control()
                return
            else:
                print("Need to download fresh copy of " + str(download_url))
                self.log_text_to_label(self.www_dl_control.ids.www_dl_label, "Downloading fresh copy of " + download_url + ".")
            
            last_update = time.time() - 3
            dots = "."
            
            start_time = time.time()

            # Alternate download -faster download speeds then w iter_content but how to get progress on long donwloads?
            #local_filename = url.split('/')[-1]
            #with requests.get(url, stream=True) as r:
            #    with open(local_filename, 'wb') as f:
            #        shutil.copyfileobj(r.raw, f)


            with open(local_file_path + ".dltmp", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep alive chunks
                        f.write(chunk)
                        current_pos += len(chunk)
                        #print("Saving " + str(len(chunk)) + " bytes")
                    else:
                        #print("Keepalive?")
                        pass
                    
                    if total_size == 0:
                        self.set_progress_value(self.www_dl_control.ids.www_dl_progress, 0)
                    else:
                        self.set_progress_value(self.www_dl_control.ids.www_dl_progress, int(float(current_pos) / float(total_size) * 100))
                    
                    if time.time() - last_update > 1:
                        dots += "."
                        if len(dots) > 5:
                            dots = "."
                        upload_speed = ""
                        elapsed_time = time.time() - start_time
                        if elapsed_time == 0:
                            elapsed_time = 1
                        transfer_speed = float(current_pos / elapsed_time)
                        if transfer_speed == 0:
                            transfer_speed = 1
                        if int(elapsed_time) != 0:
                            upload_speed = get_human_file_size(transfer_speed) + "/s"
                        still_queued = total_size - current_pos
                        time_left = str(timedelta(seconds=int(still_queued / transfer_speed)))

                        self.log_text_to_label(self.www_dl_control.ids.www_dl_label, "Downloading " + download_url + "    " + upload_speed + "  " + time_left + dots)
                        last_update = time.time()
                    
                    # Cancel button pressed?
                    if self.www_dl_in_progress is not True:
                        # Break out of the current loop.
                        break
            if self.www_dl_in_progress:
                self.www_dl_status = "Complete"
            else:
                self.www_dl_status = "Canceled"
            

            # Remove prev file if exists
            #if os.path.exists(local_file_path):
            #    os.unlink(local_file_path)
            # Move the file into place
            os.replace(local_file_path + ".dltmp", local_file_path)
            # Set local time to the time on the server
            new_time = time.mktime(url_time.timetuple())  # Convert to timestamp
            os.utime(local_file_path, (new_time, new_time))
        except Exception as ex:
            err_msg = "Error trying to download file " + str(download_url) + " -> " + str(ex)
            print(err_msg)
            self.www_dl_status = err_msg
        finally:    
            # Mark that we are done downloading
            self.www_dl_in_progress = False

        # Done w the download, close the popup
        #self.www_dl_control.dismiss()
        self.dismiss_www_dl_control()

    def cancel_www_download(self):
        # Setting this to false will let the loop fall out and stop downloading
        self.www_dl_in_progress = False
        return

    def wait_for_www_download(self, worker_thread):
        global MAIN_WINDOW, sm
        # Block and wait for download to complete but not lock current thread so kivy can still function.
        root_window = EventLoop.window #self.root.get_root_window()
              
        while worker_thread.is_alive():
            # Make sure app main loop runs so it doesn't freeze
            time.sleep(.5)
            

            # NOTE - We are in a different thread, if this freezes things, it is because
            # we are updating widgets in different threads!
            #root_window._mainloop()
            #Clock.idle()
            
            # Force a repaint?
            #root_window.refresh()
            # Slight pause...
            #print(' - wait_for_www_download sleeping...')
            
            #Clock.usleep(5000)

        return self.www_dl_status

    def update_online_server(self, status_label, run_button=None, progress_bar=None, progress_label=None):
        if run_button is not None:
            run_button.disabled = True
        # Start a thread to do the work
        self.log_text_to_label(status_label, "\n\n[b]Starting Update[/b]...")
        self.set_internet_mode('online')  # .is_online = True
        threading.Thread(target=self.update_online_server_worker, args=(status_label, run_button, progress_bar, progress_label)).start()

    def update_online_server_worker(self, status_label, run_button=None, progress_bar=None, progress_label=None):
        global progress_widget, progress_widget_label
        progress_widget = progress_bar
        progress_widget_label = progress_label

        # Get project folder (parent folder)
        root_path = os.path.dirname(get_app_folder())

        # Pull current stuff from GIT repo so we have the latest code
        self.log_text_to_label(status_label, "\n\n[b]Pulling latest updates from github...[/b]\n")
        self.git_pull_local(status_label)

        # Get the current domain name
        domain = self.config.getdefault("Online Settings", "domain", "ed")
                
        # Login to the OPE server
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection(status_label)

        if ssh is None:
            # Error connecting!
            self.log_text_to_label(status_label, "\n\n[b]SYNC ERROR[/b]\n - Unable to complete sync ")
            if err_str != "":
                self.log_text_to_label(status_label, "\n" + err_str)
            self.log_text_to_label(status_label, "\n\n[b]Exiting early!!![/b]")
            if run_button is not None:
                self.set_button_disabled(run_button, False)
            return False

        try:
            # Push local git repo to server - should auto login now
            self.log_text_to_label(status_label, "\n\n[b]Pushing github updates to OPE server[/b]\n")
            self.git_push_repo(ssh, ssh_server, ssh_user, ssh_pass, ssh_folder, status_label, online=True)
            self.set_progress_value(progress_bar, 0)
            
            # Set enabled files for apps
            self.log_text_to_label(status_label, "\n\n[b]Enabling apps[/b]\n")
            self.enable_apps(ssh, ssh_folder, status_label)

            # Download the current docker images
            self.log_text_to_label(status_label, "\n\n[b]Downloading current apps[/b]\n - downloading around 10Gig the first time...\n")
            self.pull_docker_images(ssh, ssh_folder, status_label, ssh_server, domain, ssh_pass)
            self.set_progress_value(progress_bar, 0)

            # Run the up command so the docker apps start
            self.log_text_to_label(status_label, "\n\n[b]Starting Apps[/b]\n - some apps may be slow to come online (e.g. canvas typically takes 1-5 minutes)...\n")
            self.start_apps(ssh, ssh_folder, ssh_pass, status_label, ssh_server, domain)

            # Save the image binary files for syncing
            self.log_text_to_label(status_label, "\n\n[b]Zipping Docker Apps[/b]\n - will take a few minutes...\n")
            self.save_docker_images(ssh, ssh_folder, status_label)
            self.set_progress_value(progress_bar, 0)

            # Download docker images to the USB drive
            self.log_text_to_label(status_label, "\n\n[b]Copying Docker Apps to USB drive[/b]\n - will take a few minutes...\n")
            self.copy_docker_images_to_usb_drive(ssh, ssh_folder, status_label, progress_bar)
            self.set_progress_value(progress_bar, 0)

            # Start syncing volume folders
            self.log_text_to_label(status_label, "\n\n[b]Syncing Volumes[/b]\n - may take a while...\n")
            self.sync_volumes(ssh, ssh_folder, status_label, 'online')

            ssh.close()
        except Exception as ex:
            self.log_text_to_label(status_label, "\n\n[b]SYNC ERROR[/b]\n - Unable to complete sync ")
            self.log_text_to_label(status_label, str(ex))
            self.log_text_to_label(status_label, "\n\n[b]Exiting early!!![/b]")
            print(traceback.print_exc())
            if run_button is not None:
                self.set_button_disabled(run_button, False)
            return False
            # Logger.info("Error connecting: " + str(ex))

        self.log_text_to_label(status_label, "\n\n[b]DONE[/b]")
        if run_button is not None:
            self.set_button_disabled(run_button, False)

        pass

    def update_offline_server(self, status_label, run_button=None, progress_bar=None, progress_label=None):
        if run_button is not None:
            self.set_button_disabled(run_button, True)
        # Start a thread to do the work
        self.log_text_to_label(status_label, "\n\n[b]Starting Update[/b]...")
        self.set_internet_mode('offline')  # .is_online = 0
        threading.Thread(target=self.update_offline_server_worker, args=(status_label, run_button, progress_bar, progress_label)).start()

    def update_offline_server_worker(self, status_label, run_button=None, progress_bar=None, progress_label=None):
        global progress_widget, progress_widget_label
        progress_widget = progress_bar
        progress_widget_label = progress_label

        # Get project folder (parent folder)
        root_path = os.path.dirname(get_app_folder())

        # Login to the OPE server
        # Get the current domain name
        domain = self.config.getdefault("Offline Settings", "domain", "ed")
        
        # Login to the OPE server
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection(status_label)

        if ssh is None:
            # Error connecting!
            self.log_text_to_label(status_label, "\n\n[b]SYNC ERROR[/b]\n - Unable to complete sync ")
            if err_str != "":
                self.log_text_to_label(status_label, "\n" + err_str)
            self.log_text_to_label(status_label, "\n\n[b]Exiting early!!![/b]")
            if run_button is not None:
                self.set_button_disabled(run_button, False)
            return False

        try:
            # Push local git repo to server - should auto login now
            self.log_text_to_label(status_label, "\n\n[b]Pushing repo to server[/b]\n")
            self.git_push_repo(ssh, ssh_server, ssh_user, ssh_pass, ssh_folder, status_label, online=False)
            self.set_progress_value(progress_bar, 0)

            # Set enabled files for apps
            self.log_text_to_label(status_label, "\n\n[b]Enabling Docker Apps[/b]\n")
            self.enable_apps(ssh, ssh_folder, status_label)

            # Copy images from USB to server
            self.log_text_to_label(status_label, "\n\n[b]Copying Docker Apps from USB drive[/b]\n - will take a few minutes...\n")
            self.copy_docker_images_from_usb_drive(ssh, ssh_folder, status_label, progress_bar)

            # Import the images into docker
            self.log_text_to_label(status_label, "\n\n[b]UnZipping Docker Apps[/b]\n - may take several minutes...\n")
            self.load_docker_images(ssh, ssh_folder, status_label)
            self.set_progress_value(progress_bar, 0)

            # Run the up command so the docker apps start
            self.log_text_to_label(status_label, "\n\n[b]Starting Docker Apps[/b]\n - some apps may be slow to come online (e.g. canvas)...\n")
            self.start_apps(ssh, ssh_folder, ssh_pass, status_label, ssh_server, domain)

            # Start syncing volume folders
            self.log_text_to_label(status_label, "\n\n[b]Syncing Volumes[/b]\n - may take a while...\n")
            self.sync_volumes(ssh, ssh_folder, status_label, 'offline')

            ssh.close()
        except Exception as ex:
            self.log_text_to_label(status_label, "\n\n[b]SYNC ERROR[/b]\n - Unable to complete sync ")
            self.log_text_to_label(status_label, str(ex))
            self.log_text_to_label(status_label, "\n\n[b]Exiting early!!![/b]")
            if run_button is not None:
                self.set_button_disabled(run_button, False)
            return False
            # Logger.info("Error connecting: " + str(ex))
        
        self.log_text_to_label(status_label, "\n\n[b]DONE[/b]")
        if run_button is not None:
            self.set_button_disabled(run_button, False)
        pass

    def verify_ope_server(self, status_label):
        # See if you can connect to the OPE serve and if the .ope_root file is present
        self.log_text_to_label(status_label, "starting...")
        threading.Thread(target=self.verify_ope_server_worker, args=(status_label,)).start()

    def verify_ope_server_worker(self, status_label):
        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection(status_label)
        
        if ssh is None:
            # Error connecting!
            self.log_text_to_label(status_label, "\n\n[b]SYNC ERROR[/b]\n - Unable to complete sync ")
            if ssh_error_string != "":
                self.log_text_to_label(status_label, "\n" + ssh_error_string)
            self.log_text_to_label(status_label, "\n\n[b]Exiting early!!![/b]")
            if run_button is not None:
                self.set_button_disabled(run_button, False)
            return False


        self.log_text_to_label(status_label, "Checking connection...")

        try:
            stdin, stdout, stderr = ssh.exec_command("ls -lah " + ssh_folder + " | grep .ope_root | wc -l ", get_pty=True)
            stdin.close()
            count = stdout.read().decode('utf-8').strip()
            if count == "1":
                self.log_text_to_label(status_label, "\n\nFound OPE folder - you are ready to go.")
            else:
                self.log_text_to_label(status_label, "\n\nERROR - Connection succeeded, but OPE folder not found. ")
                Logger.info("1 means found root: " + str(count))

            ssh.close()
        except Exception as ex:
            self.log_text_to_label(status_label, "\n\nERROR - Unable to connect to OPE server : " + str(ex))
            Logger.info("Error connecting: " + str(ex))

        # status_label.text += " done."

    def close_app(self):
        global APP_RUNNING
        # Signals threads/etc that app is stopping
        APP_RUNNING = False
        App.get_running_app().stop()

    def set_app_active(self, app_name, value):
        # Save the status of the app
        ret = value

        # Always return true for required apps (can't turn them off)
        if app_name in SyncOPEApp.required_apps:
            ret = "1"

        if ret is False:
            ret = "0"
        if ret is True:
            ret = "1"

        Logger.info("Setting app: " + app_name + " " + str(ret))
        self.config.set("Selected Apps", app_name, ret)
        self.config.write()

        # Make sure dependant apps are also on
        if ret == "1" and app_name in SyncOPEApp.app_depends:
            deps = SyncOPEApp.app_depends[app_name]
            Logger.info("Enabling dependant apps: " + str(deps))
            for dep in deps:
                self.set_app_active(dep, True)

        return ret

    def is_app_active(self, app_name):
        ret = self.config.getdefault("Selected Apps", app_name, "0")

        # Always return true for required apps
        if app_name in SyncOPEApp.required_apps:
            ret = "1"

        return ret

    def get_ssh_connection(self, status_label=None, show_error_popup=True, ssh_server="", ssh_user="", ssh_pass=""):
        # USAGE - ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection()
        # ssh will be None if it fails
        
        ssh_folder = ""
        err_str = ""
        if ssh_server == "" and SyncOPEApp.server_mode == 'online':
            ssh_server = self.config.getdefault("Online Settings", "server_ip", "127.0.0.1")
            ssh_user = self.config.getdefault("Online Settings", "server_user", "root")
            ssh_pass = self.get_online_pw()  # self.config.getdefault("Online Settings", "server_password", "changeme")
            ssh_folder = self.config.getdefault("Online Settings", "server_folder", "/ope")
        elif ssh_server == "" and SyncOPEApp.server_mode == 'offline':
            ssh_server = self.config.getdefault("Offline Settings", "server_ip", "127.0.0.1")
            ssh_user = self.config.getdefault("Offline Settings", "server_user", "root")
            ssh_pass = self.get_offline_pw()  # self.config.getdefault("Offline Settings", "server_password", "changeme")
            ssh_folder = self.config.getdefault("Offline Settings", "server_folder", "/ope")

        ret = None

        if status_label is not None:
            self.log_text_to_label(status_label, "\n\n[b]Connecting to OPE server[/b]\n " + ssh_user + "@" + ssh_server + "...")


        if ssh_server != "" and ssh_user != "" and ssh_pass != "":
            # Connect to server
            ssh, err_str = ssh_utils.get_ssh_connection(ssh_server, ssh_user, ssh_pass)
            ret = ssh
            # Translate ~ characters in ssh_folder
            if "~" in ssh_folder:
                sftp = ssh.open_sftp()
                h = sftp.normalize("")
                ssh_folder = ssh_folder.replace("~", h)
                sftp.close()

        if ret is None and show_error_popup is True:
            self.show_error_popup("SSH Connection Error", "Error connecting to SSH server " + str(err_str))

        return ret, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass

    @mainthread
    def show_error_popup(self, title, text):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=text))
        b = Button(text='Close', size_hint=(1, .1))
        content.add_widget(b)
        popup = Popup(title=title,
                        content=content,
                        size_hint=(None, None),
                        size=(800, 400))
        # Hook the close button to the popup dismiss method
        b.bind(on_press=popup.dismiss)
        popup.open()

    def fill_apps_dropdown(self, app_dropdown):
        if app_dropdown is None:
            return

        app_dropdown.clear_widgets()

        app_list = self.get_enabled_apps()  # ['ope-smc', 'ope-canvas']

        for a in app_list:
            b = Button(text=a, size_hint_y=None,
                       height=30, on_release=lambda btn: app_dropdown.select(btn.text))
            app_dropdown.add_widget(b)

    def get_app_info(self, app_name, status_label=None):
        t = threading.Thread(target=self.get_app_info_thread,
                             args=(app_name, status_label))
        t.start()

    def get_app_info_thread(self, app_name, status_label):
        if app_name == '':
            content = BoxLayout(orientation='vertical')
            content.add_widget(Label(
                text='Must select an app first!'))
            b = Button(text='Close', size_hint=(1, .1))
            content.add_widget(b)
            popup = Popup(title='Get App Status',
                          content=content,
                          size_hint=(None, None),
                          size=(800, 400))
            # Hook the close button to the popup dismiss method
            b.bind(on_press=popup.dismiss)
            popup.open()
            return

        popup = Popup(title='Get App Status',
                      content=Label(text='Connecting and gathering info...'),
                      size_hint=(None, None),
                      size=(800, 400),
                      auto_dismiss=False)
        popup.open()

        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection()

        if ssh is None:
            # Show dialog w error
            print("Error connecting to SSH server!")
            popup.dismiss()
            return

        # Get the logs for the app
        cmd = "cd " + ssh_folder + "; " + \
              "cd docker_build_files;" + \
              "docker-compose logs " + app_name + "; "

        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        out = ""
        out += stdout.read().decode('utf-8')
        status_label.text += color.translate_color_codes_to_markup(out)
        if 'docker-machine' in out:
            status_label.text += "[color=#ff0000]ERROR DETECTED\n   - You may need to use the \"Restart all OPE apps\" button on the previous page![/color]\n\n"

        # Get the uptime of the app
        cmd = "cd " + ssh_folder + "; " + \
            "cd docker_build_files; " + \
            "docker ps --format \"table {{.ID}}\t{{.Names}}\t{{.CreatedAt}}\t{{.RunningFor}}\t{{.Status}}\" --filter name=" + app_name + ";"
        # "docker-compose ps " + app_name + "; "
        stdin, stdout, stderr = ssh.exec_command(cmd)  # get_pty=True)
        stdin.close()
        out = ""
        out += stdout.read().decode('utf-8')
        out = "}}mn--------------------------------------------------\n" + \
              "}}mn| }}cnAPP STATUS - from docker ps}}mn   |\n" + \
              "}}mn--------------------------------------------------\n}}xx" + \
              out
        status_label.text += color.translate_color_codes_to_markup(out)

        popup.dismiss()

    def restart_docker_apps(self):
        # Start a new thread to do this work
        t = threading.Thread(target=self.restart_docker_apps_thread)
        t.start()

    def restart_docker_apps_thread(self):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(
            text='Trying to restart apps...\n\nShould take 20-60 seconds.'))
        popup = Popup(title='Apps Restarted',
                      content=content,
                      size_hint=(None, None),
                      size=(800, 400),
                      auto_dismiss=False)
        popup.open()

        ssh, ssh_folder, err_str, ssh_server, ssh_user, ssh_pass = self.get_ssh_connection()

        if ssh is None:
            # Show dialog w error
            print("Error connecting to SSH server!")
            popup.dismiss()
            return

        cmd = "cd " + ssh_folder + "; " + \
              "cd docker_build_files;" + \
              "docker-compose down; " + \
              "service docker stop; " + \
              "rm -Rf /var/run/docker.sock; " + \
              "service docker start; sleep 4; " + \
              "sh up.sh;"

        stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
        stdin.close()
        out = ""
        out += stdout.read().decode('utf-8')
        # print(out)

        popup.dismiss()

        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='Apps restarted!!!\n\n502 errors are normal during restart.\nMost apps should be live in 30 seconds,\nCanvas generally takes 3-10 minutes.'))
        b = Button(text='Close', size_hint=(1, .1))
        content.add_widget(b)
        popup = Popup(title='Apps Restarted',
                      content=content,
                      size_hint=(None, None),
                      size=(800, 400))
        # Hook the close button to the popup dismiss method
        b.bind(on_press=popup.dismiss)
        popup.open()
        pass

    def init_git_repo(self, ssh_connection=None, ope_folder=None):
        # git init
        # Set global configs like email and name
        # git config --global user.email "syncapp@correctionsed.com"
        # git config --global user.name "Sync App"
        # git stash save
        pass

    def update_sync_boxes_thread(self, router_subnet, router_pw, output_label):
        global APP_FOLDER
        if output_label is not None:
            self.log_text_to_label(output_label, "Searching for routers...\n\n")
        # Get the path to the router files
        router_files_path = os.path.join(os.path.dirname(APP_FOLDER), "router_files")

        sb = router_utils.SyncBoxes(router_files_folder=router_files_path, router_pw=router_pw,
                                    output_label=output_label)

        sb.find_routers(subnet_prefix=router_subnet)
        sb.update_routers()

    def update_sync_boxes(self, router_subnet, router_pw, output_label):
        t = threading.Thread(target=self.update_sync_boxes_thread,
                             args=(router_subnet, router_pw,
                                   output_label)).start()

    def show_settings_panel(self, panel_name):
        # Make sure settings are visible
        self.open_settings()

        # Try to find this panel
        content = self._app_settings.children[0].content
        menu = self._app_settings.children[0].menu

        curr_p = content.current_panel
        for p in content.panels:
            val = content.panels[p]
            if val.title == panel_name:
                curr_p = val

        # Set selected item
        content.current_uid = curr_p.uid
        # Show selected item in the menu
        # TODO - This manually finds the button, should be able to bind properly
        for button in menu.buttons_layout.children:
            if button.uid != curr_p.uid:
                button.selected = False
            else:
                button.selected = True
        # Bind the current_uid property to the menu
        # content.bind(current_uid=menu.on_selected_uid)
        # menu.bind(selected_uid=self._app_settings.children[0].content.current_uid)
        # content.current_uid = curr_p.uid
        # menu.selected_uid = self._app_settings.children[0].content.current_uid


# Register Objects for use in KV files
# Factory.register('FogSFTPFileSystem', cls=FogSFTPFileSystem)

if __name__ == "__main__":
    # Start the app
    SyncOPEApp().run()

