@echo off
ECHO ===============================================================================
ECHO ===============================================================================
ECHO.
ECHO This script installs security baselines into local policy for Windows 10.
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


ECHO Installing Windows 10 security settings and policies...
:: Create local directory for Exploit Protection and copy file locally
copy /y EP.xml %TEMP%
powershell.exe Set-ProcessMitigation -PolicyFilePath %TEMP%\EP.xml
del %TEMP%\EP.xml
:: Apply Windows 10 Security
Tools\LGPO.exe /v /g  ..\GPOs\{50FB9D1D-4213-434F-9FD3-DC82D8201178} > "%SECGUIDELOGS%%\Win10-install.log"
Tools\LGPO.exe /v /g  ..\GPOs\{F462100B-70FF-4A68-86B1-E73F2FE5DF37} >> "%SECGUIDELOGS%%\Win10-install.log"
echo Windows 10 Local Policy Applied


ECHO Installing Internet Explorer 11 policies...
:: Apply Internet Explorer 11 Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{4CBE0444-6C8A-42A7-866E-0A9C8DD36541} > "%SECGUIDELOGS%%\IE_11-install.log"
Tools\LGPO.exe /v /g ..\GPOs\{0C21BE77-7B39-46AB-BA2E-E4F107AFA658} >> "%SECGUIDELOGS%%\IE_11-install.log"
echo Internet Explorer 11 Local Policy Applied


ECHO Installing Windows Defender Antivirus policies...
:: Apply Windows Defender Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{6B516863-9BFE-4C98-9586-BE84AC6D5247} > "%SECGUIDELOGS%%\Windows_DefenderAV-install.log"
echo Windows Defender Antivirus Local Policy Applied


ECHO Installing Windows Credential Guard policies...
:: Apply Windows Credential Guard Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{DBBCC71D-54C4-49ED-BD2F-0748492F6CE6} > "%SECGUIDELOGS%%\Cred_Guard-install.log"
echo Windows Credential Guard Local Policy Applied


ECHO Installing Windows BitLocker policies...
:: Apply Windows BitLocker Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{3BCA33D0-559D-4F49-9E0F-B5BAF8CB2BBA} > "%SECGUIDELOGS%%\BitLocker-install.log"
echo Windows BitLocker Local Policy Applied


ECHO Installing Domain Security policies...
:: Apply Domain Security Policy
Tools\LGPO.exe /v /g ..\GPOs\{E129872A-64EE-4CB3-9493-867A87B012B0} > "%SECGUIDELOGS%%\Domain-install.log"
echo Domain Security Policy Applied


ECHO Installing Client Side Extensions...
:: Apply Client Side Extensions
Tools\LGPO.exe /v /e mitigation /e audit /e zone > "%SECGUIDELOGS%%\CSE-install.log"
echo Client Side Extensions Applied


:: Copy Custom Administrative Templates
ECHO Copying custom administrative templates
copy /y ..\Templates\*.admx %SystemRoot%\PolicyDefinitions
copy /y ..\Templates\*.adml %SystemRoot%\PolicyDefinitions\en-US

:: Disabling Scheduled Tasks
SCHTASKS.EXE /Change /TN \Microsoft\XblGameSave\XblGameSaveTask      /DISABLE

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