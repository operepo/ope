REM Much of this pulled from https://forums.fogproject.org/topic/9877/windows-10-pro-oem-sysprep-imaging/2

echo "uninstall apps we don't want..."
powershell -Command "get-appxpackage *3dbuilder* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*3dbuilder*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *alarms* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*alarms*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *appconnector* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*appconnector*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *appinstaller* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*appinstaller*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *communicationsapps* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*communicationsapps*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *camera* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*camera*” } | Remove-AppxProvisionedPackage -online'

REM powershell -Command "get-appxpackage *feedback* | remove-appxpackage"
REM powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*feedback*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *officehub* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*officehub*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *getstarted* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*getstarted*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *skypeapp* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*skypeapp*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *zunemusic* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*zunemusic*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *zune* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*zune*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *maps* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*maps*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *messaging* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*messaging*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *wallet* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*wallet*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *connectivitystore* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*connectivitystore*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *bingfinance* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*bingfinance*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *bing* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*bing*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *zunevideo* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*zunevideo*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *bingnews* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*bingnews*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *onenote* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*onenote*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *oneconnect* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*oneconnect*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *people* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*people*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *commsphone* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*commsphone*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *windowsphone* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*windowsphone*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *phone* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*phone*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *bingsports* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*bingsports*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *sticky* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*sticky*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *sway* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*sway*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *bingweather* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*bingweather*” } | Remove-AppxProvisionedPackage -online'

powershell -Command "get-appxpackage *xboxcomp* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*xboxcomp*” } | Remove-AppxProvisionedPackage -online'

REM  -- KEEP THESE APPS
REM powershell -Command "get-appxpackage *calculator* | remove-appxpackage"
REM powershell -Command "get-appxpackage *solitaire* | remove-appxpackage"
REM powershell -Command "get-appxpackage *mspaint* | remove-appxpackage"
REM powershell -Command "get-appxpackage *photos* | remove-appxpackage"
REM powershell -Command "get-appxpackage *3d* | remove-appxpackage"
REM powershell -Command "get-appxpackage *soundrecorder* | remove-appxpackage"
REM powershell -Command "get-appxpackage *holographic* | remove-appxpackage"
REM  To uninstall Windows Store: (Be very careful!)
powershell -Command "get-appxpackage *windowsstore* | remove-appxpackage"
powershell -Command 'Get-appxprovisionedpackage –online | where-object {$_.packagename –like “*windowsstore*” } | Remove-AppxProvisionedPackage -online'

echo "Disable fast boot..."s
reg ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f

echo "Turn off hibernate..."
powercfg /H off

echo "Compact OS files..."
compact /CompactOS:always

echo "Clean update files - shrink winsxs..."
Dism.exe /online /Cleanup-Image /StartComponentCleanup
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase

Dism.exe /online /Cleanup-Image /SPSuperseded

echo "Clear software distribution..."
net stop wuauserv
net stop bits
del /F /S /Q c:\windows\SoftwareDistribution\*
net start wuauserv
net start bits

echo "Zero the drive - compression works great on zeroed space (may take several hours)..."
c:\apps\sdelete\sdelete -z c:

echo "Running Chkdsk /f..."
rem chkdsk /f c:
chkntfs /C c:

echo "Time to reboot. Run PatchCleaner before reboot to trim installer folder"
echo "Enter to reboot now or CTRL+C to cancel..."
pause
REM SHUTDOWN
REM Hold SHIFT when selecting shutdown to not do fastboot.
shutdown /r /t 0







