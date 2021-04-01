@echo off
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

SET ESC=[
SET ESC_CLEAR=%ESC%2j
SET ESC_RESET=%ESC%0m
SET ESC_GREEN=%ESC%32m
SET ESC_RED=%ESC%31m
SET ESC_YELLOW=%ESC%33m

set tfile=%temp%\runasuac.vbs
rem check if we have UAC permissions
rem >nul 2>&1 "%SYSTEMROOT%\system32\icacls.exe" "%SYSTEMROOT%\system32\config\system"
NET FILE 1>NUL 2>NUL

rem error flag set = no admin priv
if '%errorlevel%' NEQ '0' (
    rem echo Not admin...
    rem use ping for slight pause
    rem set seconds=3
    rem PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1
    goto switchToUAC
) else ( goto isAlreadyUAC )

echo %ESC_RED%Why are you here - this is a bug - please report it%ESC_RESET%
rem use ping for slight pause
set seconds=4
PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1

:switchToUAC
    echo Not UAC - Switching to UAC...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%tfile%"
    echo args = "/C %~s0 %*" >> "%tfile%"
    echo For Each strArg in WScript.Arguments >> "%tfile%"
    echo   args = args ^& strArg ^& " " >> "%tfile%"
    echo Next >> "%tfile%"
    echo UAC.ShellExecute "cmd", args, "", "runas", 1 >> "%tfile%"
    
    rem wscript "%tfile%" %*
    wscript "%tfile%"
    rem echo Params  %*
    rem use ping for slight pause
    set seconds=3
    PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1
    exit /B
    
:isAlreadyUAC
    rem echo Alread Running with UAC...
    if exist "%tfile%" ( del "%tfile%" )
    pushd "%CD%"
    cd /D "%~dp0"

set MGMT_PATH=%~dp0..\mgmt.exe
rem NOTE - install_service needs to run from the tmp folder
rem  - upgrade_ope.cmd should be run from the tmp folder already, but just in case...
rem set INSTALL_SVC_PATH=%~dp0..\install_service.cmd
set INSTALL_SVC_PATH=%programdata%\ope\tmp\ope_laptop_binaries\Services\mgmt\install_service.cmd

rem Can we run mgmt.exe?
if exist %~dp0..\mgmt.py (
  rem running in development environment, run as python script
  cd %~dp0
  cd ..
  set MGMT_PATH=python "!cd!\mgmt.py"
  cd %~dp0
) 

call !MGMT_PATH! version
IF %ERRORLEVEL% NEQ 0 (
    REM Can't run? Try installing vc runtimes
    echo Unable to run MGMT.exe at !MGMT_PATH!
    rem call %~dp0..\..\..\bin\install_vc_runtimes.cmd
    rem run for both possible locations
    rem use ping for slight pause
    set seconds=10
    PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1
    exit /b 2
    rem exit /b %ERRORLEVEL%
)

rem Disable Student Accounts during any update check
echo %ESC_GREEN%Running install_service.cmd...%ESC_RESET%
call !INSTALL_SVC_PATH!
IF %ERRORLEVEL% NEQ 0 (
    REM error in credentialing
    echo.
    echo %ESC_RED%****** CRITICAL ERROR - Unable to install new OPE services *******%ESC_RESET%
    echo.
    rem run for both possible locations
    
    call !MGMT_PATH! bad_credential
    IF !ERRORLEVEL! NEQ 0 (
        rem bad call - try running from program data folder instead
        call %programdata%\ope\Services\mgmt\mgmt.exe bad_credential
    )

    rem use ping for slight pause
    set seconds=10
    PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1
    
    exit /b 2
    rem exit /b %ERRORLEVEL%
)

rem tell mgmt to finish the upgrade (re-apply security, enable student account)
echo %ESC_GREEN%**Running finish_upgrade**%ESC_RESET%
call !MGMT_PATH! finish_upgrade
IF %ERRORLEVEL% NEQ 0 (
    rem Problem finishing upgrade?
    echo.
    echo %ESC_RED%****** CRITICAL ERROR - Unable to install new OPE services *******%ESC_RESET%
    echo.
    rem run for both possible locations
    
    call !MGMT_PATH! bad_credential
    IF !ERRORLEVEL! NEQ 0 (
        rem bad call - try running from program data folder instead
        call %programdata%\ope\Services\mgmt\mgmt.exe bad_credential
    )
    
    rem use ping for slight pause
    set seconds=10
    PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1
    exit /b 2
)

rem good upgrade, return 0
rem use ping for slight pause
set seconds=3
rem PING -n !seconds! 127.0.0.1 >NUL 2>&1 || PING -n !seconds! ::1 >NUL 2>&1
echo Upgrade complete.

rem Run ping_smc to finish up syncing if needed
!MGMT_PATH! ping_smc -f
exit /b 0