@echo off
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

rem escape code for colors
SET ESC=[
SET ESC_CLEAR=%ESC%2j
SET ESC_RESET=%ESC%0m
SET ESC_GREEN=%ESC%32m
SET ESC_RED=%ESC%31m
SET ESC_YELLOW=%ESC%33m

echo %ESC_GREEN%Stopping OPEService...%ESC_RESET%
net stop OPEService
if %ERRORLEVEL% NEQ 0 (
    echo %ESC_YELLOW%STOP OPEService Failed - This isn't an issue if it is the first time you are credentialing this laptop. %ESC_RESET%
)

echo %ESC_GREEN%UnRegistering OPEService...%ESC_RESET%
%programdata%\ope\Services\OPEService\OPEService.exe remove
rem if %ERRORLEVEL% NEQ 0 (
rem     echo.
rem     echo %ESC_RED%ERROR UnRegistering OPE Service! - Something wen't VERY wrong. %ESC_RESET%
rem     echo.
    rem echo %ESC_YELLOW%Running Bad Credential Fallback%ESC_RESET%
    rem call %programdata%\ope\Services\mgmt\mgmt.exe bad_credential
rem     exit /B 2
rem )

rem need to copy the OPEService folder into the proper location

echo %ESC_GREEN%Copying latest version of Services...%ESC_RESET%
rem /Q for quiet, /F for full
SET QUIET_FLAG=/Q

if exist OPEService.py (
    rem /Q instead of F
    echo -- Copying %~dp0\dist\ to %programdata%\ope\Services\
    xcopy /ECIHRKY %QUIET_FLAG% %~dp0\dist\* %programdata%\ope\Services\ 
) else (
    echo -- Copying %~dp0\dist\ to %programdata%\ope\Services\
    xcopy /ECIHRKY %QUIET_FLAG% %~dp0\..\Services\* %programdata%\ope\Services\
    
)

rem add service to safe mode so it will boot then too
echo %ESC_GREEN%Enabling OPEService in SafeMode%ESC_RESET%
set SERVICE_NAME=OPEService
reg add "HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\%SERVICE_NAME%" /ve /F /d Service /t REG_SZ

reg add "HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Network\%SERVICE_NAME%" /ve /F /d Service /t REG_SZ

rem Install the service - ensure it is installed w the proper settings 
rem --startup
echo %ESC_GREEN%Registering OPEService...%ESC_RESET%
rem --interactive
%programdata%\ope\Services\OPEService\OPEService.exe install
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo %ESC_RED%ERROR Registering OPE Service! - Something wen't VERY wrong. %ESC_RESET%
    echo.
    echo %ESC_YELLOW%Running Bad Credential Fallback%ESC_RESET%
    call %programdata%\ope\Services\mgmt\mgmt.exe bad_credential
    exit /B 2
)

echo %ESC_GREEN%Enabling OPEService AutoRecovery Options...%ESC_RESET%
rem Set service recovery options
rem SC qfailure %SERVICE_NAME%
rem SC failure %SERVICE_NAME% reset=0 actions=restart/60000/restart/60000/run/1000
SC failure %SERVICE_NAME% reset=0 actions=restart/60000/restart/60000/reboot/1000  >> nul 2>&1
rem sc failure %SERVICE_NAME% command= ""C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" "C:\AT\MyPowerShellScript.ps1" "possibleArguments""

echo %ESC_GREEN%Starting OPEService...%ESC_RESET%
net start OPEService
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo %ESC_RED%ERROR Starting OPE Service! - Something wen't VERY wrong. %ESC_RESET%
    echo.
    echo %ESC_YELLOW%Running Bad Credential Fallback%ESC_RESET%
    call %programdata%\ope\Services\mgmt\mgmt.exe bad_credential
    exit /B 2
)

