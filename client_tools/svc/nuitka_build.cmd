@echo off
setlocal enabledelayedexpansion

:: Get today's date in yy.mm.dd format
for /f "tokens=2-4 delims=/-. " %%A in ('date /t') do (
    set year=%%C
    set month=%%A
    set day=%%B
)

:: Format the date as yy.mm.dd
set year=%year:~2,2%
set todayVersion=%year%.%month%.%day%

:: Path to the mgmt.version file
set jsonFile=mgmt.version

:: Initialize version counter
set versionSuffix=0

:: Check if the version file exists
if exist %jsonFile% (
    :: Extract the current version from the JSON file
    for /f "tokens=2 delims=:, " %%A in ('findstr /i "version" %jsonFile%') do (
        set currentVersion=%%A
        set currentVersion=!currentVersion:"=!
    )
    
    :: Split the current version to get the suffix
    for /f "tokens=1-4 delims=." %%A in ("!currentVersion!") do (
        set lastDateVersion=%%A.%%B.%%C
        set lastSuffix=%%D
    )

    :: If the last date version matches today, increment the suffix
    if "!lastDateVersion!"=="!todayVersion!" (
        set /a versionSuffix=!lastSuffix! + 1
    ) else (
        set versionSuffix=0
    )
)

:: Format the new version
set newVersion=%todayVersion%.%versionSuffix%

:: Write the new version back to the mgmt.version file
(
    echo {
    echo     "version": "%newVersion%"
    echo }
) > %jsonFile%


set VERSION=!newVersion!

:: Output the new version
rem echo Updated version is: %VERSION%


rem endlocal

echo Building mgmt.exe - %VERSION%
rem exit
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
    --file-reference-choice=runtime ^
    --mingw64 ^
    --windows-icon-from-ico=logo_icon.ico ^
    --windows-company-name=OPE_PROJECT ^
    --windows-product-name=MGMT_TOOL ^
    --windows-file-version=%VERSION% ^
    --windows-product-version=%VERSION% ^
    --windows-file-description="MGMT Tool - used to run system commands for credentialing laptops" ^
    --disable-plugin=numpy --disable-plugin=tk-inter --disable-plugin=pyqt5 --disable-plugin=pyside2 ^
    mgmt.py

echo Copying mgmt.version and rc files to dist folder
xcopy /y .\mgmt.version .\mgmt.dist\
xcopy /EQy .\rc .\mgmt.dist\rc\
