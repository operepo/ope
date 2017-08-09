REM Much of this pulled from https://forums.fogproject.org/topic/9877/windows-10-pro-oem-sysprep-imaging/2

echo "uninstall apps we don't want..."
powershell -Command "get-appxpackage *3dbuilder* | remove-appxpackage"
powershell -Command "get-appxpackage *alarms* | remove-appxpackage"
powershell -Command "get-appxpackage *appconnector* | remove-appxpackage"
powershell -Command "get-appxpackage *appinstaller* | remove-appxpackage"
powershell -Command "get-appxpackage *communicationsapps* | remove-appxpackage"
powershell -Command "get-appxpackage *camera* | remove-appxpackage"
REM powershell -Command "get-appxpackage *feedback* | remove-appxpackage"
powershell -Command "get-appxpackage *officehub* | remove-appxpackage"
powershell -Command "get-appxpackage *getstarted* | remove-appxpackage"
powershell -Command "get-appxpackage *skypeapp* | remove-appxpackage"
powershell -Command "get-appxpackage *zunemusic* | remove-appxpackage"
powershell -Command "get-appxpackage *zune* | remove-appxpackage"
powershell -Command "get-appxpackage *maps* | remove-appxpackage"
powershell -Command "get-appxpackage *messaging* | remove-appxpackage"
powershell -Command "get-appxpackage *wallet* | remove-appxpackage"
powershell -Command "get-appxpackage *connectivitystore* | remove-appxpackage"
powershell -Command "get-appxpackage *bingfinance* | remove-appxpackage"
powershell -Command "get-appxpackage *bing* | remove-appxpackage"
powershell -Command "get-appxpackage *zunevideo* | remove-appxpackage"
powershell -Command "get-appxpackage *bingnews* | remove-appxpackage"
powershell -Command "get-appxpackage *onenote* | remove-appxpackage"
powershell -Command "get-appxpackage *oneconnect* | remove-appxpackage"
powershell -Command "get-appxpackage *people* | remove-appxpackage"
powershell -Command "get-appxpackage *commsphone* | remove-appxpackage"
powershell -Command "get-appxpackage *windowsphone* | remove-appxpackage"
powershell -Command "get-appxpackage *phone* | remove-appxpackage"
powershell -Command "get-appxpackage *bingsports* | remove-appxpackage"
powershell -Command "get-appxpackage *sticky* | remove-appxpackage"
powershell -Command "get-appxpackage *sway* | remove-appxpackage"
powershell -Command "get-appxpackage *bingweather* | remove-appxpackage"
powershell -Command "get-appxpackage *xboxcomp* | remove-appxpackage"

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







