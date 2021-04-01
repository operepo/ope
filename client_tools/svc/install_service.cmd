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


rem slight pause, let mgmt finish and exit
rem use ping for slight pause
set seconds=6
PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1

echo %ESC_GREEN%Stopping OPEService...%ESC_RESET%
net stop OPEService
if %ERRORLEVEL% NEQ 0 (
    echo %ESC_YELLOW%STOP OPEService Failed - This isn't an issue if it is the first time you are credentialing this laptop. %ESC_RESET%
)

PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1

echo %ESC_GREEN%Stoping any running LMS apps...%ESC_RESET%
taskkill /f /im OPE_LMS.exe   1>NUL 2>NUL

echo %ESC_GREEN%Stoping any running mgmt apps...%ESC_RESET%
taskkill /f /im mgmt.exe   1>NUL 2>NUL

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

echo %ESC_GREEN%Slight pause for things to shut down...%ESC_RESET%
rem use ping for slight pause
set seconds=15
PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1


echo %ESC_GREEN%Copying latest version of Services...%ESC_RESET%
rem /Q for quiet, /F for full
SET QUIET_FLAG=/Q

if exist %~dp0OPEService.py (
    rem /Q instead of F
    echo -- Clearing old GPO files %programdata%\ope\Services\mgmt\rc\gpo
    rmdir /S /Q %programdata%\ope\Services\mgmt\rc\gpo

    echo -- Copying %~dp0\dist\ to %programdata%\ope\Services\
    xcopy /ECIHRKY %QUIET_FLAG% %~dp0\dist\* %programdata%\ope\Services\ 
) else (
    rem running from mgmt folder
    echo -- Clearing old GPO files %programdata%\ope\Services\mgmt\rc\gpo
    rmdir /S /Q %programdata%\ope\Services\mgmt\rc\gpo

    echo -- Copying %~dp0\..\ to %programdata%\ope\Services\
    xcopy /ECIHRKY %QUIET_FLAG% %~dp0\..\* %programdata%\ope\Services\
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
%programdata%\ope\Services\OPEService\OPEService.exe --startup auto install
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo %ESC_RED%ERROR Registering OPE Service! - Something wen't VERY wrong. %ESC_RESET%
    echo.
    echo %ESC_YELLOW%Running Bad Credential Fallback%ESC_RESET%
    call %programdata%\ope\Services\mgmt\mgmt.exe bad_credential
    rem use ping for slight pause
    set seconds=10
    PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1

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
    rem use ping for slight pause
    set seconds=10
    PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1

    exit /B 2
)

rem good run - return 0
rem use ping for slight pause
rem set seconds=5
rem PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1

exit /B 0