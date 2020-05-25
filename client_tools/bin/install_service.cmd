@echo off

net stop OPEService

rem need to copy the OPEService folder into the proper location

if exist OPEService.py (
    rem echo In dev folder  %~dp0
    rem %~dp0\dist\svc\OPEService.exe -install -auto -interactive
    rem /Q instead of F
    xcopy /ECIHRKY /Q %~dp0\dist\* %programdata%\ope\Services\
) else (
    rem echo In binary folder
    rem %~dp0\..\svc\OPEService.exe -install -auto -interactive
    xcopy /ECIHRKY /F %~dp0\..\Services\* %programdata%\ope\Services\
    
)

rem add service to safe mode so it will boot then too
set SERVICE_NAME=OPEService
reg add "HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\%SERVICE_NAME%" /ve /F /d Service /t REG_SZ

reg add "HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Network\%SERVICE_NAME%" /ve /F /d Service /t REG_SZ

rem Install the service - ensure it is installed w the proper settings 
%programdata%\ope\Services\OPEService\OPEService.exe install --startup auto --interactive

net start OPEService