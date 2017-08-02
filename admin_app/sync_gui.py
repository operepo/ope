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

# Adjust kivy config to change window look/behavior
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
# Keep a reference to the main window
MAIN_WINDOW = None


def get_home_folder():
    home_path = expanduser("~")
    return home_path

# Find the base folder to store data in - use the home folder
BASE_FOLDER = os.path.join(get_home_folder(), ".ope")
# Make sure the .ope folder exists
if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER, 0o770)


# Define how we should migrate database tables
lazy_tables = False
fake_migrate_all = False
fake_migrate = False
migrate = True

# Progress bar used by threaded apps
progress_widget = None


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
    # s = re.sub(r"(?m)^[-+*]\s+(.*)$", translate("~[list]\n[*]%s\n[/list]"), s)
    # s = re.sub(r"(?m)^\d+\.\s+(.*)$", translate("~[list=1]\n[*]%s\n[/list]"), s)
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

    def sync_online_volume(self, volume, folder, ssh, ssh_folder, status_label, branch="master"):
        pass

    def sync_offline_volume(self, volume, folder, ssh, ssh_folder, status_label, branch="master"):
        # Sync files on the online server with the USB drive

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        volumes_path = os.path.join(root_path, "volumes")
        volume_path = os.path.join(volumes_path, volume)
        folder_path = os.path.join(volume_path, folder.replace("/", os.pathsep))

        # Figure the path for the git app
        git_path = os.path.join(root_path, "PortableGit/bin/git.exe")

        # Ensure the folder exists on the USB drive
        try:
            os.makedirs(folder_path)
        except:
            # will error if folder already exists
            pass

        # Ensure the folder exists on the server
        remote_folder_path = os.path.join(ssh_folder, "volumes", volume, folder).replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("mkdir -p " + remote_folder_path, get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        status_label.text += "[b]Syncing Volue: [/b]" + volume + "/" + folder
        sftp = ssh.open_sftp()

        # Copy remote files to the USB drive
        r_cwd = remote_folder_path
        for f in sftp.listdir_iter(r_cwd):
            status_label.text += str(f)

        # Walk the local folder and see if there are files that don't exist that should be copied
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                status_label.text += "Processing " + file



        sftp.close()

        # self.sync_online_volume('canvas', 'tmp/files')

    def git_pull_local(self, status_label, branch="master"):
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
        proc = subprocess.Popen(git_path + " pull ope_origin " + branch, stdout=subprocess.PIPE)
        for line in proc.stdout:
            status_label.text += line
        #ret += proc.stdout.read()

        return ret

    def git_push_repo(self, ssh, ssh_server, ssh_user, ssh_pass, ssh_folder, status_label, online=True, branch="master", ):
        ret = ""
        remote_name = "ope_online"
        if online is not True:
            remote_name = "ope_offline"

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # Figure the path for the git app
        git_path = os.path.join(root_path, "PortableGit/bin/git.exe")

        # Set current path
        os.chdir(root_path)

        # Ensure the folder exists, is a repo, and has a sub folder (ope.git) that is a bare repo
        ret += "\n\n[b]Ensuring git repo setup properly...[/b]\n"
        stdin, stdout, stderr = ssh.exec_command("mkdir -p " + ssh_folder + "; cd " + ssh_folder + "; git init; mkdir -p ope.git; cd ope.git; git init --bare;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        # Ensure that local changes are stash/saved so that the pull works later
        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git stash;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        # Make sure the remote is added to local repo
        proc = subprocess.Popen(git_path + " remote remove " + remote_name, stdout=subprocess.PIPE)
        for line in proc.stdout:
            status_label.text += line

        ssh_bare_repo_path = os.path.join(ssh_folder, "ope.git").replace("\\","/")
        proc = subprocess.Popen(git_path + " remote add " + remote_name + " ssh://" + ssh_user + "@" + ssh_server + ":" + ssh_bare_repo_path, stdout=subprocess.PIPE)
        for line in proc.stdout:
            status_label.text += line

        # Push to the remote server
        proc = subprocess.Popen(git_path + " push " + remote_name + " " + branch, stdout=subprocess.PIPE)
        for line in proc.stdout:
            status_label.text += line

        # Have remote server checkout from the bare repo
        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git remote remove local_bare;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git remote add local_bare ope.git;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        stdin, stdout, stderr = ssh.exec_command("cd " + ssh_folder + "; git pull local_bare " + branch + ";", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        return ret

    def get_enabled_apps(self):
        # Return a list of enabled apps

        # Start with required apps
        apps = ["ope-gateway", "ope-dns", "ope-clamav", "ope-redis", "ope-postgresql"]

        # Check each item to see if it is enabled
        if self.config.getdefault("Selected Apps", "ope-fog", "1") == "1":
            apps.append("ope-fog")
        if self.config.getdefault("Selected Apps", "ope-canvas", "1") == "1":
            apps.append("ope-canvas")
        if self.config.getdefault("Selected Apps", "ope-smc", "1") == "1":
            apps.append("ope-smc")
        if self.config.getdefault("Selected Apps", "ope-coco", "0") == "1":
            apps.append("ope-coco")
        if self.config.getdefault("Selected Apps", "ope-freecodecamp", "0") == "1":
            apps.append("ope-freecodecamp")
        if self.config.getdefault("Selected Apps", "ope-gcf", "0") == "1":
            apps.append("ope-gcf")
        if self.config.getdefault("Selected Apps", "ope-jsbin", "0") == "1":
            apps.append("ope-jsbin")
        if self.config.getdefault("Selected Apps", "ope-kalite", "0") == "1":
            apps.append("ope-kalite")
        if self.config.getdefault("Selected Apps", "ope-rachel", "0") == "1":
            apps.append("ope-rachel")
        if self.config.getdefault("Selected Apps", "ope-stackdump", "0") == "1":
            apps.append("ope-stackdump")
        if self.config.getdefault("Selected Apps", "ope-wamap", "0") == "1":
            apps.append("ope-wamap")

        return apps

    def enable_apps(self, ssh, ssh_folder, status_label):
        ret = ""
        # Get the list of enabled apps
        apps = self.get_enabled_apps()

        # Clear all the enabled files
        stdin, stdout, stderr = ssh.exec_command("rm -f " + ssh_folder + "/docker_build_files/ope-*/.enabled", get_pty=True)
        stdin.close()
        r = stdout.read()
        if len(r) > 0:
            status_label.text += "\n" + r

        for a in apps:
            status_label.text += "\n-- Enabling App: " + a
            app_path = os.path.join(ssh_folder, "docker_build_files", a)
            enabled_file = os.path.join(app_path, ".enabled")
            enable_cmd = "mkdir -p " + app_path + "; touch " + enabled_file
            stdin, stdout, stderr = ssh.exec_command(enable_cmd.replace('\\', '/'), get_pty=True)
            stdin.close()
            r = stdout.read()
            if len(r) > 0:
                status_label.text += "\n" + r
        status_label.text += "...."
        return ret

    def generate_local_ssh_key(self, status_label):
        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Make sure ssh keys exist (saved in home directory in .ssh folder on current computer)
        bash_path = os.path.join(root_path, "PortableGit/bin/bash.exe")
        # Run this to generate keys
        proc = subprocess.Popen(bash_path + " -c 'if [ ! -f ~/.ssh/id_rsa ]; then ssh-keygen -t rsa -f ~/.ssh/id_rsa; fi'", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        try:
            proc.stdin.write("\n\n")  #  Write 2 line feeds to add empty passphrase
        except:
            # This will fail if it isn't waiting for input, that is ok
            pass
        proc.stdin.close()
        for line in proc.stdout:
            status_label.text += line
        #ret += proc.stdout.read()

    def add_ssh_key_to_authorized_keys(self, ssh, status_label):
        ret = ""

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Make sure ssh keys exist (saved in home directory in .ssh folder on current computer)
        bash_path = os.path.join(root_path, "PortableGit/bin/bash.exe")

        # Make sure remote server has .ssh folder
        stdin, stdout, stderr = ssh.exec_command("mkdir -p ~/.ssh; chmod 700 ~/.ssh;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        # Find the server home folder
        stdin, stdout, stderr = ssh.exec_command("cd ~; pwd;", get_pty=True)
        stdin.close()
        server_home_dir = stdout.read()
        if server_home_dir is None:
            server_home_dir = ""
        server_home_dir = server_home_dir.strip()

        # Add ssh keys to server for easy push/pull later
        # bash -- cygpath -w ~   to get win version of home directory path
        proc = subprocess.Popen(bash_path + " -c 'cygpath -w ~'", stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        proc.stdin.close()
        home_folder = proc.stdout.read().strip()
        # home_folder = get_home_folder() #  expanduser("~")
        rsa_pub_path = os.path.join(home_folder, ".ssh", "id_rsa.pub")
        sftp = ssh.open_sftp()
        sftp.put(rsa_pub_path, os.path.join(server_home_dir, ".ssh/id_rsa.pub.ope").replace("\\", "/"))
        sftp.close()
        # Make sure we remove old entries
        stdin, stdout, stderr = ssh.exec_command("awk '{print $3}' ~/.ssh/id_rsa.pub.ope", get_pty=True)
        stdin.close()
        remove_host = stdout.read()
        stdin, stdout, stderr = ssh.exec_command("sed -i '/" + remove_host.strip() + "/d' ~/.ssh/authorized_keys", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        # Add id_rsa.pub.ope to the authorized_keys file
        stdin, stdout, stderr = ssh.exec_command("cat ~/.ssh/id_rsa.pub.ope >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line


        # Last step - make sure that servers key is accepted here so we don't get warnings
        known_hosts_path = os.path.join(home_folder, ".ssh", "known_hosts" )
        ssh.save_host_keys(known_hosts_path)

        return ret

    def pull_docker_images(self, ssh, ssh_folder, status_label):
        # Run on the online server - pull the current docker images
        ret = ""

        # Need to re-run the rebuild_compose.py file
        rebuild_path = os.path.join(ssh_folder, "build_tools", "rebuild_compose.py").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("python " + rebuild_path, get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        # Run the rebuild
        docker_files_path = os.path.join(ssh_folder, "docker_build_files").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("cd " + docker_files_path + "; docker-compose pull;", get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        return ret

    def save_docker_images(self, ssh, ssh_folder, status_label):
        # Dump docker images to the app_images folder on the server
        ret = ""

        # Run the script that is on the server
        save_script = os.path.join(ssh_folder, "sync_tools", "export_docker_images.py").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("python " + save_script, get_pty=True)
        stdin.close()
        for line in stdout:
            status_label.text += line

        return ret

    def load_docker_images(self, ssh, ssh_folder, status_label):
        # Dump docker images to the app_images folder on the server
        ret = ""

        load_script = os.path.join(ssh_folder, "sync_tools", "import_docker_images.py").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("python " + load_script, get_pty=True)
        stdin.close()
        for line in stdout.read():
            status_label.text += line

        return ret

    def copy_docker_images_to_usb_drive(self, ssh, ssh_folder, status_label, progress_bar):
        global progress_widget

        progress_widget = progress_bar

        # Copy images from online server to usb drive
        ret = ""

        # Ensure the local app_images folder exists
        try:
            os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images"))
        except:
            # Throws an error if already exists
            pass

        # Use the list of enabled images
        apps = self.get_enabled_apps()

        sftp = ssh.open_sftp()

        # Check each app to see if we need to copy it
        for app in apps:
            progress_bar.value = 0
            # Download the server digest file
            online_digest = "."
            current_digest = "..."
            remote_digest_file = os.path.join(ssh_folder, "volumes", "app_images", app + ".digest").replace("\\", "/")
            local_digest_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images", app + ".digest.online")
            current_digest_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images", app + ".digest")
            remote_image = os.path.join(ssh_folder, "volumes", "app_images", app + ".tar").replace("\\", "/")
            local_image = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images", app + ".tar")
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
            if online_digest != current_digest:
                status_label.text += "\nCopying App: " + app
                sftp.get(remote_image, local_image, callback=self.copy_docker_images_to_usb_drive_progress_callback)
                # Logger.info("Moving on...")
                # Store the current digest
                try:
                    f = open(current_digest_file, "w")
                    f.write(online_digest)
                    f.close()
                except:
                    status_label.text += "Error saving current digest: " + current_digest_file
            else:
                status_label.text += "\nApp hasn't changed, skipping: " + app
            #

        sftp.close()
        return ret

    def copy_docker_images_to_usb_drive_progress_callback(self, transferred, total):
        global progress_widget

        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        if total == 0:
            progress_widget.value = 0
        else:
            progress_widget.value = int(float(transferred) / float(total) * 100)

    def copy_docker_images_from_usb_drive(self, ssh, ssh_folder, status_label, progress_bar):
        global progress_widget

        progress_widget = progress_bar

        # Copy images from usb drive to the offline server
        ret = ""

        # Ensure the local app_images folder exists
        try:
            os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images"))
        except:
            # Throws an error if already exists
            pass

        # Ensure that server has app_images folder
        app_images_path = os.path.join(ssh_folder, "volumes", "app_images").replace("\\", "/")
        stdin, stdout, stderr = ssh.exec_command("mkdir -p " + app_images_path, get_pty=True)
        stdin.close()
        ret += stdout.read()

        # Use the list of enabled images
        apps = self.get_enabled_apps()

        sftp = ssh.open_sftp()

        # Check each app to see if we need to copy it
        for app in apps:
            progress_bar.value = 0
            # Download the server digest file
            offline_digest = "."
            current_digest = "..."
            remote_digest_file = os.path.join(ssh_folder, "volumes", "app_images", app + ".digest").replace("\\", "/")
            local_digest_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images", app + ".digest.offline")
            current_digest_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images", app + ".digest")
            remote_image = os.path.join(ssh_folder, "volumes", "app_images", app + ".tar").replace("\\", "/")
            local_image = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "volumes", "app_images", app + ".tar")
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
                status_label.text += "\nCopying App: " + app
                sftp.put(local_image, remote_image, callback=self.copy_docker_images_from_usb_drive_progress_callback)
                # Logger.info("Moving on...")
                # Store the current digest
                try:
                    f = open(local_digest_file, "w")
                    f.write(current_digest)
                    f.close()
                except:
                    status_label.text += "Error saving current digest: " + current_digest_file
            else:
                status_label.text += "\nApp hasn't changed, skipping: " + app
            #

        sftp.close()
        return ret

    def copy_docker_images_from_usb_drive_progress_callback(self, transferred, total):
        global progress_widget

        # Logger.info("XFerred: " + str(transferred) + "/" + str(total))
        if total == 0:
            progress_widget.value = 0
        else:
            progress_widget.value = int(float(transferred) / float(total) * 100)

    def update_online_server(self, status_label, run_button=None, progress_bar=None):
        if run_button is not None:
            run_button.disabled = True
        # Start a thread to do the work
        status_label.text = "[b]Starting Update[/b]..."
        threading.Thread(target=self.update_online_server_worker, args=(status_label, run_button, progress_bar)).start()

    def update_online_server_worker(self, status_label, run_button=None, progress_bar=None):

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # Pull current stuff from GIT repo so we have the latest code
        status_label.text += "\n\n[b]Git Pull[/b]\nPulling latest updates from github...\n"
        status_label.text += self.git_pull_local(status_label)

        # Login to the OPE server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_server = self.config.getdefault("Online Settings", "server_ip", "127.0.0.1")
        ssh_user = self.config.getdefault("Online Settings", "server_user", "root")
        ssh_pass = self.get_online_pw()  # self.config.getdefault("Online Settings", "server_password", "")
        ssh_folder = self.config.getdefault("Online Settings", "server_folder", "/ope")
        status_label.text += "\n\n[b]SSH Connection[/b]\nConnecting to " + ssh_user + "@" + ssh_server + "..."

        try:
            # Connect to the server
            ssh.connect(ssh_server, username=ssh_user, password=ssh_pass)

            # Make sure we have an SSH key to use for logins
            self.generate_local_ssh_key(status_label)

            # Add our ssh key to the servers list of authorized keys
            self.add_ssh_key_to_authorized_keys(ssh, status_label)

            # Push local git repo to server - should auto login now
            status_label.text += "\n\n[b]Pushing repo to server[/b]\n"
            self.git_push_repo(ssh, ssh_server, ssh_user, ssh_pass, ssh_folder, status_label, online=True)
            progress_bar.value = 0

            # Set enabled files for apps
            status_label.text += "\n\n[b]Enabling apps[/b]\n"
            self.enable_apps(ssh, ssh_folder, status_label)

            # Download the current docker images
            status_label.text += "\n\n[b]Downloading current apps[/b]\n - downloading around 10Gig the first time...\n"
            self.pull_docker_images(ssh, ssh_folder, status_label)
            progress_bar.value = 0

            # Save the image binary files for syncing
            status_label.text += "\n\n[b]Save app binaries[/b]\n - will take a few minutes...\n"
            self.save_docker_images(ssh, ssh_folder, status_label)
            progress_bar.value = 0

            # Download docker images to the USB drive
            status_label.text += "\n\n[b]Downloading images to USB drive[/b]\n - will take a few minutes...\n"
            self.copy_docker_images_to_usb_drive(ssh, ssh_folder, status_label, progress_bar)
            progress_bar.value = 0


            # Start syncing volume folders
            # - sync canvas files
            self.sync_online_volume('canvas', 'tmp/files', ssh, ssh_folder, status_label)

            # - sync canvas db
            #self.sync_online_volume('canvas', 'db/sync')



            # TODO TODO TODO
            # - sync smc

            # - sync coco

            # - sync rachel

            ssh.close()
        except Exception as ex:
            status_label.text += "\n\n[b]SSH ERROR[/b]\n - Unable to connect to OPE server : " + str(ex)
            status_label.text += "\n\n[b]Exiting early!!![/b]"
            if run_button is not None:
                run_button.disabled = False
            return False
            # Logger.info("Error connecting: " + str(ex))

        status_label.text += "\n\n[b]DONE[/b]"
        if run_button is not None:
            run_button.disabled = False

        pass

    def update_offline_server(self, status_label, run_button=None, progress_bar=None):
        if run_button is not None:
            run_button.disabled = True
        # Start a thread to do the work
        status_label.text = "[b]Starting Update[/b]..."
        threading.Thread(target=self.update_offline_server_worker, args=(status_label, run_button, progress_bar)).start()

    def update_offline_server_worker(self, status_label, run_button=None, progress_bar=None):

        # Get project folder (parent folder)
        root_path = os.path.dirname(os.path.dirname(__file__))

        # Login to the OPE server
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_server = self.config.getdefault("Offline Settings", "server_ip", "127.0.0.1")
        ssh_user = self.config.getdefault("Offline Settings", "server_user", "root")
        ssh_pass = self.get_offline_pw()  # self.config.getdefault("Offline Settings", "server_password", "")
        ssh_folder = self.config.getdefault("Offline Settings", "server_folder", "/ope")
        status_label.text += "\n\n[b]SSH Connection[/b]\nConnecting to " + ssh_user + "@" + ssh_server + "..."

        try:
            # Connect to the server
            ssh.connect(ssh_server, username=ssh_user, password=ssh_pass)

            self.sync_offline_volume('canvas', 'tmp/files', ssh, ssh_folder, status_label)
            status_label.text += "[b]DEBUG DEBUG DEBUB [/b]"
            ssh.close()
            return

            # Make sure we have an SSH key to use for logins
            self.generate_local_ssh_key(status_label)

            # Add our ssh key to the servers list of authorized keys
            self.add_ssh_key_to_authorized_keys(ssh, status_label)

            # Push local git repo to server - should auto login now
            status_label.text += "\n\n[b]Pushing repo to server[/b]\n"
            self.git_push_repo(ssh, ssh_server, ssh_user, ssh_pass, ssh_folder, status_label, online=False)
            progress_bar.value = 0

            # Set enabled files for apps
            status_label.text += "\n\n[b]Enabling apps[/b]\n"
            self.enable_apps(ssh, ssh_folder, status_label)

            # Copy images from USB to server
            status_label.text += "\n\n[b]Downloading images to USB drive[/b]\n - will take a few minutes...\n"
            self.copy_docker_images_from_usb_drive(ssh, ssh_folder, status_label, progress_bar)

            # Import the images into docker
            status_label.text += "\n\n[b]Load app binaries[/b]\n - will take a few minutes...\n"
            self.load_docker_images(ssh, ssh_folder, status_label)
            progress_bar.value = 0

            # Start syncing volume folders
            # - sync canvas
            self.sync_offline_volume('canvas', 'tmp/files', ssh, ssh_folder, status_label)
            # TODO TODO TODO
            # - sync smc

            # - sync coco

            # - sync rachel

            ssh.close()
        except Exception as ex:
            status_label.text += "\n\n[b]SSH ERROR[/b]\n - Unable to connect to OPE server : " + str(ex)
            status_label.text += "\n\n[b]Exiting early!!![/b]"
            if run_button is not None:
                run_button.disabled = False
            return False
            # Logger.info("Error connecting: " + str(ex))


        status_label.text += "\n\n[b]DONE[/b]"
        if run_button is not None:
            run_button.disabled = False

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
