
set VERSION=1.0.0
set COMPANY_NAME=OpenPrisonEducation
set PRODUCT_NAME=sync_media_files
set DESCRIPTION="Sync Media Files to SMC"
set MAIN_FILE=sync_media_files.py
set OUT_FILE=sync_media_files.exe
set DATA_FILE=""
rem build mgmt
rem --windows-disable-console   - if running gui
rem --windows-icon-from-ico=logo_icon.ico
rem --windows-uac-admin  -- force uac prompt
rem --windows-uac-uiaccess    --- ???
rem --windows-company-name=%COMPANY_NAME%
rem --windows-product-name=%PRODUCT_NAME%
rem --windows-file-version=%VERSION%
rem --windows-product-version=%VERSION%
rem --windows-file-description=%DESCRIPTION%
rem --windows-onefile-tempdir  -- use temp folder rather then appdata folder
rem --python-flag=
rem --follow-imports
rem --onefile  - use appdata folder to unpack
rem --windows-dependency-tool=pefile  - collect dependancies if needed
rem --experimental=use_pefile_recurse --experimental=use_pefile_fullrecurse   --- to find more depends if needed

rem python -m nuitka --python-arch=x86 --standalone  %MAIN_FILE%
rem arch   x86 or x86_64
rem --follow-imports ^

rem --windows-disable-console ^

rem --onefile ^
rem --windows-onefile-tempdir-spec=%TEMP%\\matrix_%PID%_%TIME%\\^
rem --enable-plugin=anti-bloat ^

rem -o %OUT_FILE% ^
rem python -m nuitka ^
python -m nuitka ^
    --python-flag=no_site ^
    --standalone ^
    --windows-icon-from-ico=logo_icon.ico ^
    --windows-company-name=%COMPANY_NAME% ^
    --windows-product-name=%PRODUCT_NAME% ^
    --windows-file-version=%VERSION% ^
    --windows-product-version=%VERSION% ^
    --windows-file-description=%DESCRIPTION% ^
    --disable-plugin=numpy --disable-plugin=tk-inter --disable-plugin=pyqt5 --disable-plugin=pyside2 ^
    %MAIN_FILE%

