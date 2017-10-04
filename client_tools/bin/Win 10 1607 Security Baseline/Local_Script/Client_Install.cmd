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
:: Apply Windows 10 Security
Tools\LGPO.exe /v /g  ..\GPOs\{F6584239-28E8-4F44-B860-08FEDD241565} > "%SECGUIDELOGS%%\Win10-install.log"
Tools\LGPO.exe /v /g  ..\GPOs\{EB965378-F079-41EE-AF63-54900D1D771C} >> "%SECGUIDELOGS%%\Win10-install.log"
echo Windows 10 Local Policy Applied


ECHO Installing Internet Explorer 11 policies...
:: Apply Internet Explorer 11 Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{07177AF8-97DF-407D-89A6-C875CD1784BC} > "%SECGUIDELOGS%%\IE_11-install.log"
Tools\LGPO.exe /v /g ..\GPOs\{B0AA555D-B555-4832-9BA6-2D5A973A7B92} >> "%SECGUIDELOGS%%\IE_11-install.log"
echo Internet Explorer 11 Local Policy Applied


ECHO Installing Windows Defender policies...
:: Apply Windows Defender Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{4095647A-14FE-4CE4-955A-F2311B0D62D1} > "%SECGUIDELOGS%%\Windows_Defender-install.log"
echo Windows Defender Local Policy Applied


ECHO Installing Windows Credential Guard policies...
:: Apply Windows Credential Guard Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{714FD77E-8FDD-4CB0-B3F7-FF49815473FF} > "%SECGUIDELOGS%%\Cred_Guard-install.log"
echo Windows Credential Guard Local Policy Applied


ECHO Installing Windows BitLocker policies...
:: Apply Windows BitLocker Local Policy
Tools\LGPO.exe /v /g ..\GPOs\{23D00834-1B40-4F45-A461-8F833529994C} > "%SECGUIDELOGS%%\BitLocker-install.log"
echo Windows BitLocker Local Policy Applied


ECHO Installing Domain Security policies...
:: Apply Domain Security Policy
Tools\LGPO.exe /v /g ..\GPOs\{1D2C9D38-6BB1-4C90-B5EB-2850EA18AE06} > "%SECGUIDELOGS%%\Domain-install.log"
echo Domain Security Policy Applied


ECHO Installing Client Side Extensions...
:: Apply Client Side Extensions
Tools\LGPO.exe /v /e mitigation /e audit /e zone > "%SECGUIDELOGS%%\CSE-install.log"
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