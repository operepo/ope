@echo off

rem Disable/Remove the OPE service
rem call remove_service.cmd

rem ** NOT USING CUSTOM MESSAGE SOURCE **
rem echo Building Event Viewer Message Source
rem path=%path%;C:\Users\ray\AppData\Local\Programs\Common\Microsoft\Visual C++ for Python\9.0\VC\Bin\amd64
rem path=%path%;C:\Users\ray\AppData\Local\Programs\Common\Microsoft\Visual C++ for Python\9.0\WinSDK\Bin\x64;
rem convert to res file
rem mc mgmt_EventLogMessages.mc
rem compile res file
rem rc -r -fo mgmt_EventLogMessages.res mgmt_EventLogMessages.rc
rem turn into a dll
rem link -dll -noentry -out:mgmt_EventLogMessages.dll mgmt_EventLogMessages.res

rem goto endofscript

rem For AV false positive, try clear __pycache__, build, dist and recompile
rem https://python.plainenglish.io/pyinstaller-exe-false-positive-trojan-virus-resolved-b33842bd3184

echo Removing build folders...
rd /S /Q %~dp0__pycache__
rd /S /Q %~dp0dist
rd /S /Q %~dp0build


echo Building OPE Service
python build_svc.py

echo Building OPE SShot
python build_sshot.py

echo Building OPE Mgmt Utility
python build_mgmt.py

echo Building Lock Screen Widget
python build_lock_screen_widget.py

echo "Build complete"
pause

:endofscript
