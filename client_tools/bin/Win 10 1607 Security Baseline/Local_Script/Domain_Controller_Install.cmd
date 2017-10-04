@echo off
ECHO ===============================================================================
ECHO ===============================================================================
ECHO.
ECHO This script installs security baselines into local policy for Windows Server 2016 Member Server.
ECHO.
ECHO Press Ctrl+C to stop the installation, or press any other key to continue...
ECHO.
ECHO ===============================================================================
ECHO ===============================================================================
PAUSE > nul

:: Make the directory where this script lives the current dir.
PUSHD %~dp0
SET SECGUIDE=%CD%
SET SECGUIDELOGS=%SECGUIDE%\LOGS
MD "%SECGUIDELOGS%" 2> nul


ECHO Installing Windows Server 2016 Domain Controller security settings and policies...
:: Apply Windows Server 2016 Member Server Security
Tools\LGPO.exe /v /g  ..\GPOs\{37BBB33A-A159-427D-AD58-67B1BE126AD6} > "%SECGUIDELOGS%%\Win16DC-install.log"
echo Windows Server 2016 Domain Controller Local Policy Applied


ECHO Installing Windows Defender policies...
:: Apply Windows Defender Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{4095647A-14FE-4CE4-955A-F2311B0D62D1} > "%SECGUIDELOGS%%\Windows_Defender-install.log"
echo Windows Defender Local Policy Applied


ECHO Installing Windows Credential Guard policies...
:: Apply Windows Credential Guard Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{714FD77E-8FDD-4CB0-B3F7-FF49815473FF} > "%SECGUIDELOGS%%\Cred_Guard-install.log"
echo Windows Credential Guard Local Policy Applied


ECHO Installing Domain Security policies...
:: Apply Domain Security Policy
Tools\LGPO.exe /v /g ..\GPOs\{1D2C9D38-6BB1-4C90-B5EB-2850EA18AE06} > "%SECGUIDELOGS%%\Domain-install.log"
echo Domain Security Policy Applied


ECHO Installing Client Side Extensions...
:: Apply Client Side Extensions
Tools\LGPO.exe /v /e mitigation /e audit > "%SECGUIDELOGS%%\CSE-install.log"
echo Client Side Extensions Applied


:: Copy Custom Administrative Templates
ECHO Copying custom administrative templates
copy /y ..\Templates\*.admx %SystemRoot%\PolicyDefinitions
copy /y ..\Templates\*.adml %SystemRoot%\PolicyDefinitions\en-US


::Display Notifications
ECHO.
ECHO.
ECHO ===============================================================================
ECHO ===============================================================================
ECHO.
ECHO In order to test properly, create a new non-administrative user account and
ECHO reboot.
ECHO.
ECHO Additionally, check log files located in this directory:
ECHO.    %SECGUIDELOGS%
ECHO.
ECHO Feedback can be directed to the following:  SecGuide@Microsoft.com
ECHO.
ECHO ===============================================================================
ECHO ===============================================================================
ECHO.
POPD