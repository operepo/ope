
set VERSION=1.0.1
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


rem --plugin-enable=tk-inter ^

python -m nuitka ^
    --standalone ^
    --mingw64 ^
    --plugin-enable=pyqt5 ^
    --plugin-enable=numpy ^
    --windows-disable-console ^
    --windows-icon-from-ico=logo_icon.ico ^
    --windows-company-name=OPE_PROJECT ^
    --windows-product-name=LOCK_SCREEN_WIDGET ^
    --windows-file-version=%VERSION% ^
    --windows-product-version=%VERSION% ^
    --windows-file-description="OPE Lock Screen Widget" ^
    lock_screen_widget.py

