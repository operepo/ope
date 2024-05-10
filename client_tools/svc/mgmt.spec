# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mgmt.py'],
    pathex=[],
    binaries=[],
    datas=[('logo_icon.ico', '.'), ('rc', 'rc'), ('mgmt.version', '.'), ('install_service.cmd', '.')],
    hiddenimports=['sip', 'win32timezone', 'simplejson'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [('v', None, 'OPTION')],
    exclude_binaries=True,
    name='mgmt',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='mgmt',
)
