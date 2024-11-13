
@echo off
set VERSION=24.9.5.0


python -m nuitka ^
    --standalone ^
    --file-reference-choice=runtime ^
    --mingw64 ^
    --windows-icon-from-ico=logo_icon.ico ^
    --windows-company-name=OPE_PROJECT ^
    --windows-product-name=SyncAPp ^
    --windows-file-version=%VERSION% ^
    --windows-product-version=%VERSION% ^
    --windows-file-description="Admin SyncApp - deploy or update OPE servers." ^
    --disable-plugin=numpy --disable-plugin=tk-inter --disable-plugin=pyqt5 --disable-plugin=pyside2 ^
    --include-package=kivy --include-package=requests --enable-plugin=kivy --include-package=kivy.uix.recycleview ^
    --include-data-file="C:\Python311\share\angle\bin\*.dll=./" ^
    --include-data-file="*.kv=./" ^
    --include-data-file="*.json=./" ^
    --include-data-file="*.ico=./" ^
    --include-data-file="*.png=./" ^
    --include-data-file="*.md=./" ^
    --follow-imports ^
    --output-filename=SyncApp.exe ^
    sync_gui.py


rem --include-data-file="C:\Python311\share\angle\bin\*.dll=./" ^
rem --include-data-file="C:\Python311\share\glew\bin\*.dll=./" ^
rem --include-data-file="C:\Python311\share\sdl2\bin\*.dll=./" ^

rem assets = [("SyncOPEApp.kv", "."), ("OfflineServerSettings.json", "."), ("OnlineServerSettings.json", "."),
rem          ("logo_icon.ico", "."), ("logo_icon.png", "."), ("GettingStarted.md", "."),
rem          ("version.json", "."), ("eCasas.json", "."), ("ReleaseNotes.md", ".") ]

echo Copying resource files to dist folder
rem xcopy /y .\*.kv .\sync_gui.dist\
rem xcopy /y .\*.json .\sync_gui.dist\
rem xcopy /y .\*.ico .\sync_gui.dist\
rem xcopy /y .\*.png .\sync_gui.dist\
rem xcopy /y .\*.md .\sync_gui.dist\
rem xcopy /yS C:\Python311\Lib\site-packages\kivy\data\* .\kivy_install\data\
xcopy /yS C:\Python311\Lib\site-packages\kivy\uix\* .\sync_gui.dist\kivy\uix\