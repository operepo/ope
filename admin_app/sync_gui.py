import json
import os
import sys
from os.path import expanduser

import threading
import time
from datetime import datetime

from gluon import DAL, Field
from gluon.validators import *

import kivy

from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.config import ConfigParser
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.settings import SettingString
from kivy.config import Config
from kivy.properties import ListProperty
from kivy.logger import Logger
from kivy.lang import Builder
kivy.require('1.9.2')


MAIN_WINDOW = None


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


# === Password Box (masked ***) ===
class PasswordLabel(Label):
    pass


class SettingPassword(SettingString):
    def _create_popup(self, instance):
        super(SettingPassword, self)._create_popup(instance)
        self.textinput.password = True

    def add_widget(self, widget, *largs):
        if self.content is None:
            super(SettingString, self).add_widget(widget, *largs)
        if isinstance(widget, PasswordLabel):
            return self.content.add_widget(widget, *largs)


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


    def build(self):
        global MAIN_WINDOW

        self.icon = 'logo_icon.png'
        self.settings_cls = SettingsWithSidebar
        MAIN_WINDOW = MainWindow()

        # Make sure to load current settings
        self.load_current_settings()

        # Populate data
        self.populate()

        return MAIN_WINDOW

    def build_config(self, config):
        # Default settings
        config.setdefaults("Build Settings",
                           {'build_folder': '~',
                            })
        config.setdefaults("Transfer Settings", {})

        config.setdefaults("Development Settings", {})

        config.setdefaults("Production Settings", {})

    def build_settings(self, settings):
        # Register custom settings type
        settings.register_type('password', SettingPassword)

        settings.add_json_panel('Source Settings', self.config, 'BuildSettings.json')
        settings.add_json_panel('Transfer Settings', self.config, 'TransferSettings.json')
        settings.add_json_panel('Development Settings', self.config, 'DevelopmentSettings.json')
        settings.add_json_panel('Production Settings', self.config, 'ProductionSettings.json')

    def on_config_change(self, config, section, key, value):
        Logger.info("App.on_config_change: {0}, {1}, {2}, {3}".format(config, section, key, value))

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
