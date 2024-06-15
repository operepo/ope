
@echo off
echo Use pyinstaller or opeservice - nuitka doesn't work with services w/out commercial license.
exit

set VERSION=1.0.109
@REM rem read version file from mgmt.version
@REM for /f "delims=" %%a in (mgmt.version) do (
@REM     rem strip off extra characters
@REM     echo %%a
@REM     set s=a
@REM     call set s=%%a:version=test%%
@REM     rem call set s=%%s::=%%
@REM     rem call set s=%%s:"=%%
@REM     echo %s%
@REM     if not "%%s"=="" (
@REM         set VERSION=%%s
@REM     )
@REM )
@REM echo Building mgmt.exe - %VERSION%
@REM exit
rem build mgmt
rem --windows-disable-console   - if running gui
rem --windows-icon-from-ico=logo_icon.ico
rem --windows-uac-admin  -- force uac prompt
rem --windows-uac-uiaccess    --- ???
rem --windows-company-name=OPE_PROJECT
rem --windows-product-name=MGMT_TOOL
rem --windows-file-version=%VERSION%
rem --windows-product-version=%VERSION%
rem --windows-file-description="MGMT Tool - used to run system commands for credentialing laptops"
rem --windows-onefile-tempdir  -- use temp folder rather then appdata folder
rem --python-flag=
rem --follow-imports
rem --onefile  - use appdata folder to unpack
rem --windows-dependency-tool=pefile  - collect dependancies if needed
rem --experimental=use_pefile_recurse --experimental=use_pefile_fullrecurse   --- to find more depends if needed

rem python -m nuitka --python-arch=x86 --standalone  mgmt.py

rem --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow ^
rem --nofollow-import-to=tkinter --nofollow-import-to=pyqt5 --nofollow-import-to=numpy ^

python -m nuitka ^
    --standalone ^
    --mingw64 ^
    --windows-icon-from-ico=logo_icon.ico ^
    --windows-company-name=OPE_PROJECT ^
    --windows-product-name=OPEService ^
    --windows-file-version=%VERSION% ^
    --windows-product-version=%VERSION% ^
    --windows-file-description="OPEService - OPE Service Utility" ^
    --disable-plugin=numpy --disable-plugin=tk-inter --disable-plugin=pyqt5 --disable-plugin=pyside2 ^
    --include-module="win32timezone" ^
    OPEService.py

rem Need pythoservice in the folder for this to work
rem xcopy /y C:\Python311\Lib\site-packages\win32\pythonservice.exe .\OPEService.dist\

rem xcopy /y .\mgmt.version .\mgmt.dist\
