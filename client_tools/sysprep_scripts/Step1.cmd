@echo off

REM Much of this pulled from https://forums.fogproject.org/topic/9877/windows-10-pro-oem-sysprep-imaging/2

rem disable win store auto updates which can break sysprep
reg add HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\WindowsStore /v AutoDownload /t REG_DWORD /d 2 /f


rem remove firstboot profile
echo removing firstboot profile...
wmic /node:localhost path win32_UserProfile where LocalPath="c:\\users\\firstboot" Delete 2>>c:\windows\setup\sysprep_scripts\wmic.err

rem see win10_fix.cmd for ways to fix things

echo Do you want to remove unneeded apps? [default N in 6 seconds]?
choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipappxremoval
echo uninstalling apps we don't want...

SET keep_apps="appconnector", "appinstaller", "alarms", "communicationsapps", "feedback", "getstarted", "skypeapp", "zunemusic", "zune", "maps", "messaging", "wallet", "connectivitystore", "bing", "zunevideo", "onenote", "oneconnect", "people", "commsphone", "windowsphone", "phone", "sticky", "sway", "xboxcomp", "calculator", "solitaire", "mspaint", "photos", "3d", "soundrecorder", "holographic", "windowsstore"
SET uninstall_apps="3dbuilder", "alarms", "camera", "officehub", "bingfinance", "bingnews", "bingsports", "bingweather"

(FOR %%A IN (%uninstall_apps%) DO (
    echo Uninstalling %%~A
    
    powershell -Command "get-appxpackage *%%~A* " | remove-appxpackage"
    powershell -Command "Get-appxprovisionedpackage -online | where-object {$_.packagename -like '*%%~A*' } " | Remove-AppxProvisionedPackage -online"
    
))

:skipappxremoval


rem disable windows installing these apps
reg add HKLM\Software\Policies\Microsoft\Windows\CloudContent /v DisableWindowsConsumerFeatures /t REG_DWORD /d 1 /f


echo Disable fast boot...
reg ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f

echo Do you want to compact the windows image? [recommended but takes 5 to 10 minutes - default N in 6 seconds]?
choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipcompact
echo Compact OS files...
compact /CompactOS:always
:skipcompact

echo Do you want to clean up the windows image? [recommended but takes 10 to 30 minutes - default N in 6 seconds]?
choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipcomponentcleanup
echo Clean update files - shrink winsxs...
Dism.exe /online /Cleanup-Image /StartComponentCleanup
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase
Dism.exe /online /Cleanup-Image /SPSuperseded
:skipcomponentcleanup

echo "Clear software distribution..."
net stop wuauserv
net stop bits
del /F /S /Q c:\windows\SoftwareDistribution\*
net start wuauserv
net start bits

echo Do you want to zero the drive [recommended but takes hours - default N in 6 seconds]?
choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipzero
echo Writing zeros to the drive...
rem c:\windows\setup\sysprep_scripts\sdelete\sdelete -z c:
:skipzero

echo Do you want to run chkdisk [recommended - default y in 6 seconds]?
choice /C yn /T 6 /D y /M "Press n for no, or y to run chkdsk"
if errorlevel 2 goto skipchkdsk
echo Enabling Chkdsk on reboot...
rem chkdsk /f c:
rem use chkntfs to schedule the check on reboot
chkntfs /C c:
:skipchkdsk

echo Time to reboot. Run PatchCleaner before reboot to trim installer folder
echo Do you want to run reboot now [recommended]?
choice /C yn /M "Press n for no, or y to reboot"
if errorlevel 2 goto skipreboot
REM SHUTDOWN
REM Hold SHIFT when selecting shutdown to not do fastboot.
shutdown /r /t 0
:skipreboot






