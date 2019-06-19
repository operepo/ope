import os
from os.path import join

from kivy import kivy_data_dir
from kivy.deps import sdl2, glew, angle
from kivy.tools.packaging import pyinstaller_hooks as hooks
from kivy.uix.label import Label

block_cipher = None
kivy_deps_all = hooks.get_deps_all()
kivy_factory_modules = hooks.get_factory_modules()

datas = [('SyncOPEApp.kv', '.'), ('OfflineServerSettings.json', '.'), ('OnlineServerSettings.json', '.'), ('logo_icon.ico', '.'), ('logo_icon.png', '.'), ('GettingStarted.md', '.'), ('version.json', '.'), ('eCasas.json', '.') ]

# list of modules to exclude from analysis
excludes = ['Tkinter', '_tkinter', 'twisted', 'pygments']

# list of hiddenimports
hiddenimports = kivy_deps_all['hiddenimports'] + kivy_factory_modules

# binary data
sdl2_bin_tocs = [Tree(p) for p in sdl2.dep_bins]
glew_bin_tocs = [Tree(p) for p in glew.dep_bins]
angle_bin_tocs = [Tree(p) for p in angle.dep_bins]
bin_tocs = sdl2_bin_tocs + glew_bin_tocs + angle_bin_tocs

# assets
kivy_assets_toc = Tree(kivy_data_dir, prefix=join('kivy_install', 'data'))
source_assets_toc = []
assets_toc = [kivy_assets_toc, source_assets_toc]

tocs = bin_tocs + assets_toc

a = Analysis(['sync_gui.py'],
             pathex=[os.path.dirname(os.path.abspath("."))],
             binaries=None,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             # noarchive=False)
             )
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SyncApp',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='logo_icon.ico'
          )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               *tocs,
               strip=False,
               upx=True,
               name='SyncApp')

# Use this for onefile dist
#exe = EXE(pyz,
#          a.scripts,
#          a.binaries,
#          a.zipfiles,
#          a.datas,
#          name='SyncApp',
#          debug=False,
#          strip=False,
#          upx=True,
#          runtime_tmpdir=None,
#          console=True,
#          icon='logo_icon.ico'
#          )

