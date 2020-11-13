# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['sync_media_files.py'],
             pathex=['C:\\Users\\ray\\Desktop\\git_projects\\ope\\ope\\media_files_tool'],
             binaries=[],
             datas=[],
             hiddenimports=['sip', 'win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='sync_media_files',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='sync_media_files')
