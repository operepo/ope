import json
import os
import sys
import re
from os.path import expanduser
import paramiko
import uuid
import subprocess

from security import Enc

import threading
import time
from datetime import datetime

from gluon import DAL, Field
from gluon.validators import *

import kivy

from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.settings import SettingString
from kivy.uix.settings import SettingItem
from kivy.uix.button import Button
from kivy.config import Config
Config.set('kivy', 'exit_on_escape', '0')
from kivy.properties import ListProperty
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
kivy.require('1.9.2')

# Config.set('graphics','borderless',1)
# Config.set('graphics','resizable',0)
# Config.set('graphics','position','custom')
# Config.set('graphics','left',500)
# Config.set('graphics','top',10)

# Config.set('graphics', 'resizeable', '0')
# Config.set('graphics', 'borderless', '1')
# Window.size = (900, 800)
# Window.borderless = True


# Manage multiple screens
sm = ScreenManager()

MAIN_WINDOW = None

#PW_POPUP = Popup(title='Enter Password',
#                 content=TextInput)

# Find the base folder to store data in - use the home folder
BASE_FOLDER = os.path.join(expanduser("~"), ".print_app")
# Make sure the .r2 folder exists
if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER, 0o770)


# Define how we should migrate database tables
lazy_tables = False
fake_migrate_all = False
fake_migrate = False
migrate = True


# == Database Functions ==
def connect_db(init_schema=True):
    db_file = os.path.join(BASE_FOLDER, "sync.db")
    con = DAL('sqlite://' + db_file, pool_size=10, check_reserved=['all'], lazy_tables=lazy_tables, fake_migrate=fake_migrate, fake_migrate_all=fake_migrate_all, migrate=migrate)  # fake_migrate_all=True
    con.executesql('PRAGMA journal_mode=WAL')

    if init_schema is True:
        init_db_schema(con)

    return con


def init_db_schema(db=None):
    if db is None:
        db = connect_db(False)

    # DB Schema
    # Entries

    # List of known entries
    #db.define_table("sync_folders",
    #                Field("locale_id", default=0),
    #
    #                )
    #sql = """CREATE INDEX IF NOT EXISTS `idx_sync_folders` ON `sync_folders`
    #    (`folder` ASC);"""
    db.executesql(sql)

    db.commit()
    # db.close()


# Convert markdown code to bbcode tags so they draw properly in labels
def markdown_to_bbcode(s):
    links = {}
    codes = []
    def gather_link(m):
        links[m.group(1)]=m.group(2); return ""
    def replace_link(m):
        return "[url=%s]%s[/url]" % (links[m.group(2) or m.group(1)], m.group(1))
    def gather_code(m):
        codes.append(m.group(3)); return "[code=%d]" % len(codes)
    def replace_code(m):
        return "%s" % codes[int(m.group(1)) - 1]

    def translate(p="%s", g=1):
        def inline(m):
            s = m.group(g)
            s = re.sub(r"(`+)(\s*)(.*?)\2\1", gather_code, s)
            s = re.sub(r"\[(.*?)\]\[(.*?)\]", replace_link, s)
            s = re.sub(r"\[(.*?)\]\((.*?)\)", "[url=\\2]\\1[/url]", s)
            s = re.sub(r"<(https?:\S+)>", "[url=\\1]\\1[/url]", s)
            s = re.sub(r"\B([*_]{2})\b(.+?)\1\B", "[b]\\2[/b]", s)
            s = re.sub(r"\B([*_])\b(.+?)\1\B", "[i]\\2[/i]", s)
            return p % s
        return inline

    s = re.sub(r"(?m)^\[(.*?)]:\s*(\S+).*$", gather_link, s)
    s = re.sub(r"(?m)^    (.*)$", "~[code]\\1[/code]", s)
    s = re.sub(r"(?m)^(\S.*)\n=+\s*$", translate("~[size=24][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^(\S.*)\n-+\s*$", translate("~[size=18][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^#\s+(.*?)\s*#*$", translate("~[size=24][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^##\s+(.*?)\s*#*$", translate("~[size=18][b]%s[/b][/size]"), s)
    s = re.sub(r"(?m)^###\s+(.*?)\s*#*$", translate("~[b]%s[/b]"), s)
    s = re.sub(r"(?m)^####\s+(.*?)\s*#*$", translate("~[b]%s[/b]"), s)
    s = re.sub(r"(?m)^> (.*)$", translate("~[quote]%s[/quote]"), s)
    #s = re.sub(r"(?m)^[-+*]\s+(.*)$", translate("~[list]\n[*]%s\n[/list]"), s)
    #s = re.sub(r"(?m)^\d+\.\s+(.*)$", translate("~[list=1]\n[*]%s\n[/list]"), s)
    s = re.sub(r"(?m)^((?!~).*)$", translate(), s)
    s = re.sub(r"(?m)^~\[", "[", s)
    s = re.sub(r"\[/code]\n\[code(=.*?)?]", "\n", s)
    s = re.sub(r"\[/quote]\n\[quote]", "\n", s)
    s = re.sub(r"\[/list]\n\[list(=1)?]\n", "", s)
    s = re.sub(r"(?m)\[code=(\d+)]", replace_code, s)

    return s


# Main screen
class StartScreen(Screen):
    pass


# Screen with getting starte info
class GettingStartedScreen(Screen):
    pass


class VerifySettingsScreen(Screen):
    pass


class PickAppsScreen(Screen):
    pass


class OnlineModeScreen(Screen):
    pass


class OfflineModeScreen(Screen):
    pass


class OnlineUpdateScreen(Screen):
    pass


class OfflineUpdateScreen(Screen):
    pass


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
        super(SettingItem, self).__init__(**kwargs)
        for aButton in kwargs["buttons"]:
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


class MainWindow(BoxLayout):

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

    def on_touch_up(self, touch):
        # Logger.info("main.py: MainWindow: {0}".format(touch))
        pass


class SyncOPEApp(App):
    use_kivy_settings = False

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
        e = Enc(key)
        pw = e.decrypt(pw)
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
        e = Enc(key)
        pw = e.decrypt(pw)
        return pw

    def set_online_pw(self, pw):
        self.ensure_key()
        key = self.config.getdefault("Server", "auth1", "")
        e = Enc(key)
        pw = e.encrypt(str(pw))
        self.config.set("Server", "auth3", pw)
        self.config.write()

    def build(self):
        global MAIN_WINDOW

        self.icon = 'logo_icon.png'
        self.title = "Open Prison Education"
        self.settings_cls = SettingsWithSidebar
        MAIN_WINDOW = MainWindow()

        # Make sure to load current settings
        self.load_current_settings()

        # Populate data
        self.populate()

        # Add screens for each window we can use
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(GettingStartedScreen(name="getting_started"))
        sm.add_widget(VerifySettingsScreen(name="verify_settings"))
        sm.add_widget(PickAppsScreen(name="pick_apps"))
        sm.add_widget(OnlineModeScreen(name="online_mode"))
        sm.add_widget(OfflineModeScreen(name="offline_mode"))
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(OnlineUpdateScreen(name="online_update"))
        sm.add_widget(OfflineUpdateScreen(name="offline_update"))

        sm.current = "start"
        return sm  # MAIN_WINDOW

    def build_config(self, config):
        # Default settings
        config.setdefaults("Server",
                           {})
        config.setdefaults("Online Settings",
                           {'server_ip': '127.0.0.1',
                            'server_user': 'root',
                            'server_folder': '/ope'})
        config.setdefaults("Offline Settings",
                           {'server_ip': '127.0.0.1',
                            'server_user': 'root',
                            'server_folder': '/ope'})
        config.setdefaults("Selected Apps",
                           {'ope-gateway': '1',
                            'ope-dns': '1',
                            'ope-clamav': '1',
                            'ope-redis': '1',
                            'ope-postgresql': '1',
                            'ope-fog': '1',
                            'ope-canvas': '1',
                            'ope-smc': '1',
                            'ope-coco': '0',
                            'ope-freecodecamp': '0',
                            'ope-gcf': '0',
                            'ope-jsbin': '0',
                            'ope-kalite': '0',
                            'ope-rachel': '0',
                            'ope-stackdump': '0',
                            'ope-wamap': '0',

                            })

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

        settings.add_json_panel('Online Settings', self.config, 'OnlineServerSettings.json')
        settings.add_json_panel('Offline Settings', self.config, 'OfflineServerSettings.json')

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

    def git_pull_local(self):
        ret = ""
        # Pull the latest git data to the current project folder

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # Figure the path for the git app
        git_path = os.path.join(root_path, "PortableGit/bin/git.exe")

        # Set current path
        os.chdir(root_path)

        # == Make sure we have current copy of GIT repo on USB drive
        # make sure current store is a git repo
        # git init - OK to run more than once, just do it
        proc = subprocess.Popen(git_path + " init", stdout=subprocess.PIPE)
        ret += proc.stdout.read()

        # Make sure we have proper remote settings
        proc = subprocess.Popen(git_path + " remote remove ope_origin", stdout=subprocess.PIPE)
        ret += proc.stdout.read()
        proc = subprocess.Popen(git_path + " remote add ope_origin https://github.com/operepo/ope.git", stdout=subprocess.PIPE)
        ret += proc.stdout.read()

        # Make sure we have the current stuff
        proc = subprocess.Popen(git_path + " pull ope_origin master", stdout=subprocess.PIPE)
        ret += proc.stdout.read()

        # At this point we should have the current stuff locally
        # Push to remove server
        # proc = subprocess.Popen(git_path + " remote remove ope_origin", stdout=subprocess.PIPE)
        # ret += proc.stdout.read()
        # proc = subprocess.Popen(git_path + " remote add ope_origin https://github.com/operepo/ope.git", stdout=subprocess.PIPE)
        # ret += proc.stdout.read()

        return ret

    def git_push_repo(self, ssh_server, ssh_user, ssh_pass, ssh_folder):
        ret = ""

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # Figure the path for the git app
        git_path = os.path.join(root_path, "PortableGit/bin/git.exe")

        # Set current path
        os.chdir(root_path)

        # Make sure the remote is in place
        proc = subprocess.Popen(git_path + " remote remove ope_online", stdout=subprocess.PIPE)
        ret += proc.stdout.read()
        proc = subprocess.Popen(git_path + " remote add ope_online ssh://" + ssh_user, stdout=subprocess.PIPE)
        ret += proc.stdout.read()
        # Push to the remote
        return ret

    def enable_apps(self, ssh, ssh_folder):
        ret = ""
        # Make a list of enabled apps
        ret += "\nEnabling default apps: gateway, dns, clamav, redis, postgresql"
        apps = ["ope-gateway", "ope-dns", "ope-clamav", "ope-redis", "ope-postgresql"]

        # Check each item to see if it is enabled
        if self.config.getdefault("Selected Apps", "ope-fog", "1") == "1":
            ret += "\nEnabling fog"
            apps.append("ope-fog")
        if self.config.getdefault("Selected Apps", "ope-canvas", "1") == "1":
            ret += "\nEnabling canvas"
            apps.append("ope-canvas")
        if self.config.getdefault("Selected Apps", "ope-smc", "1") == "1":
            ret += "\nEnabling smc"
            apps.append("ope-smc")
        if self.config.getdefault("Selected Apps", "ope-coco", "0") == "1":
            ret += "\nEnabling code combat"
            apps.append("ope-coco")
        if self.config.getdefault("Selected Apps", "ope-freecodecamp", "0") == "1":
            ret += "\nEnabling free code camp"
            apps.append("ope-freecodecamp")
        if self.config.getdefault("Selected Apps", "ope-gcf", "0") == "1":
            ret += "\nEnabling gcf"
            apps.append("ope-gcf")
        if self.config.getdefault("Selected Apps", "ope-jsbin", "0") == "1":
            ret += "\nEnabling jsbin"
            apps.append("ope-jsbin")
        if self.config.getdefault("Selected Apps", "ope-kalite", "0") == "1":
            ret += "\nEnabling kalite"
            apps.append("ope-kalite")
        if self.config.getdefault("Selected Apps", "ope-rachel", "0") == "1":
            ret += "\nEnabling rachel"
            apps.append("ope-rachel")
        if self.config.getdefault("Selected Apps", "ope-stackdump", "0") == "1":
            ret += "\nEnabling stackdump"
            apps.append("ope-stackdump")
        if self.config.getdefault("Selected Apps", "ope-wamap", "0") == "1":
            ret += "\nEnabling wamap"
            apps.append("ope-wamap")

        # Clear all the enabled files
        stdin, stdout, stderr = ssh.exec_command("rm -f " + ssh_folder + "/ope-*/.enabled", get_pty=True)
        stdin.close()
        r = stdout.read()
        if len(r) > 0:
            ret += "\n" + r

        for a in apps:
            app_path = os.path.join(ssh_folder, "docker_build_files", a)
            enabled_file = os.path.join(app_path, ".enabled")
            enable_cmd = "mkdir -p " + app_path + "; touch " + enabled_file
            stdin, stdout, stderr = ssh.exec_command(enable_cmd.replace('\\', '/'), get_pty=True)
            stdin.close()
            r = stdout.read()
            if len(r) > 0:
                ret += "\n" + r
        ret += "...."
        # cmd = "cd " + ssh_folder + "/docker_build_files; rm -f ope-*/.enabled; " + enable_cmd
        # ret += "\n\n[b]CMD:[/b] " + cmd + "\n\n"
        # stdin, stdout, stderr = ssh.exec_command("ls -l", get_pty=True)
        # stdin.close()
        # ret += "\n" + stdout.read()

        return ret

    def update_online_server(self, status_label):
        # Start a thread to do the work
        status_label.text = "[b]Starting Update[/b]..."
        threading.Thread(target=self.update_online_server_worker, args=(status_label,)).start()

    def update_online_server_worker(self, status_label):

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # Pull current stuff from GIT repo so we have the latest code
        status_label.text += "\n\n[b]Git Pull[/b]\nPulling latest updates from github...\n"
        status_label.text += self.git_pull_local()

        # Login to the OPE server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_server = self.config.getdefault("Online Settings", "server_ip", "127.0.0.1")
        ssh_user = self.config.getdefault("Online Settings", "server_user", "root")
        ssh_pass = self.get_online_pw() #  self.config.getdefault("Online Settings", "server_password", "")
        ssh_folder = self.config.getdefault("Online Settings", "server_folder", "/ope")
        status_label.text += "\n\n[b]SSH Connection[/b]\nConnecting to " + ssh_user + "@" + ssh_server + "..."

        try:
            # Connect to the server
            ssh.connect(ssh_server, username=ssh_user, password=ssh_pass)

            # Ensure the folder exists, is a repo, and has a sub folder (ope.git) that is a bare repo
            status_label.text += "\n\n[b]Ensuring git repo setup properly...[/b]\n"
            stdin, stdout, stderr = ssh.exec_command("mkdir -p " + ssh_folder + "; cd " + ssh_folder + "; git init; mkdir -p ope.git; cd ope.git; git init --bare;", get_pty=True)
            stdin.close()
            status_label.text += stdout.read()

            # Make sure ssh keys exist (saved in home directory in .ssh folder on current computer)
            bash_path = os.path.join(root_path, "PortableGit/bin/bash.exe")
            # Run this to generate keys
            proc = subprocess.Popen(bash_path + " -c 'if [ ! -f ~/.ssh/id_rsa ]; then ssh-keygen -t rsa -f ~/.ssh/id_rsa; fi'", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            proc.stdin.write("\n\n")  #  Write 2 line feeds to add empty passphrase
            proc.stdin.close()
            status_label.text += proc.stdout.read()

            # Add ssh keys to server for easy push/pull later


            # Push local git repo to server
            status_label.text += "\n\n[b]Pushing repo to server[/b]\n"
            status_label.text += self.git_push_repo(ssh_server, ssh_user, ssh_pass, ssh_folder)

            # Set enabled files for apps
            status_label.text += "\n\n[b]Enabling apps[/b]\n"
            status_label.text += self.enable_apps(ssh, ssh_folder)



            # # At this point if folder doesn't exit there is  a problem
            # stdin, stdout, stderr = ssh.exec_command("ls -lah " + ssh_folder + " | grep .ope_root | wc -l ", get_pty=True)
            # stdin.close()
            # count = stdout.read().strip()
            # if count == "1":
            #     status_label.text += "\n\nFound OPE folder - you are ready to go."
            # else:
            #     status_label.text += "\n\nERROR - Connection succeeded, but OPE folder not found. "
            #     # Logger.info("1 means found root: " + str(count))

            ssh.close()
        except Exception as ex:
            status_label.text += "\n\n[b]SSH ERROR[/b]\n - Unable to connect to OPE server : " + str(ex)
            status_label.text += "\n\n[b]Exiting early!!![/b]"
            return False
            # Logger.info("Error connecting: " + str(ex))


        # Start syncing volume folders
        # - sync canvas

        # - sync smc

        # - sync coco

        # - sync rachel

        status_label.text += "[b]DONE[/b]"

        pass

    def verify_ope_server(self, status_label):
        # See if you can connect to the OPE serve and if the .ope_root file is present
        status_label.text += "starting..."
        threading.Thread(target=self.verify_ope_server_worker, args=(status_label,)).start()

    def verify_ope_server_worker(self, status_label):
        ssh_server = self.config.getdefault("Online Settings", "server_ip", "127.0.0.1")
        ssh_user = self.config.getdefault("Online Settings", "server_user", "root")
        ssh_pass = self.config.getdefault("Online Settings", "server_password", "")
        ssh_folder = self.config.getdefault("Online Settings", "server_folder", "/ope")

        status_label.text = "Checking connection..."

        try:
            ssh.connect(ssh_server, username=ssh_user, password=ssh_pass)
            stdin, stdout, stderr = ssh.exec_command("ls -lah " + ssh_folder + " | grep .ope_root | wc -l ", get_pty=True)
            stdin.close()
            count = stdout.read().strip()
            if count == "1":
                status_label.text += "\n\nFound OPE folder - you are ready to go."
            else:
                status_label.text += "\n\nERROR - Connection succeeded, but OPE folder not found. "
                Logger.info("1 means found root: " + str(count))

            ssh.close()
        except Exception as ex:
            status_label.text += "\n\nERROR - Unable to connect to OPE server : " + str(ex)
            Logger.info("Error connecting: " + str(ex))

        # status_label.text += " done."

    def close_app(self):
        App.get_running_app().stop()

    def set_app_active(self, app_name, value):
        # Save the status of the app
        ret = value

        # Always return true for required apps (can't turn them off)
        if app_name == "ope-dns":
            ret = "1"
        elif app_name == "ope-gateway":
            ret = "1"
        elif app_name == "ope-clamav":
            ret = "1"
        elif app_name == "ope-postgresql":
            ret = "1"
        elif app_name == "ope-redis":
            ret = "1"

        if ret is False:
            ret = "0"
        if ret is True:
            ret = "1"

        Logger.info("Setting app: " + app_name + " " + str(ret))
        self.config.set("Selected Apps", app_name, ret)
        self.config.write()
        return ret


    def is_app_active(self, app_name):
        ret = self.config.getdefault("Selected Apps", app_name, "0")

        # Always return true for required apps
        if app_name == "ope-dns":
            ret = "1"
        elif app_name == "ope-gateway":
            ret = "1"
        elif app_name == "ope-clamav":
            ret = "1"
        elif app_name == "ope-postgresql":
            ret = "1"
        elif app_name == "ope-redis":
            ret = "1"

        return ret

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
        #content.bind(current_uid=menu.on_selected_uid)
        #menu.bind(selected_uid=self._app_settings.children[0].content.current_uid)
        #content.current_uid = curr_p.uid
        #menu.selected_uid = self._app_settings.children[0].content.current_uid


if __name__ == "__main__":
    # Start the app
    SyncOPEApp().run()


# === Build process ===

# = ClamAV =
# Standard docker build - just enable and do typical build/up

# === Sync to USB process ===
# = ClamAV =
# TODO - Have clam av sync to get new virus patterns from internet
# run this on build server:  docker exec -it ope-clamav /dl_virus_defs.sh
# 1 way sync from volumes folder - build -> USB


# === Sync to development process ===

# = ClamAV =
# 1 way sync from volumes folder - USB -> Server

# === Sync to production process ===
# Same as sync development process just point to a different server
