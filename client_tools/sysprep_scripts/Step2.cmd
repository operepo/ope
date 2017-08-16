REM  After reboot (TWICE!!! for chkdsk to finish?) run this script to sysprep
@echo off

echo Turn off hibernate...
powercfg /H off

rem remove firstboot profile
echo removing firstboot profile...
wmic /node:localhost path win32_UserProfile where LocalPath="c:\\users\\firstboot" Delete 2>>c:\apps\sysprep_scripts\wmic.err

rem delete shadow copies
echo deleting shadow copies...
vssadmin delete shadows /All /Quiet

rem Delete hidden win install files
echo clearing win install files...
rem del %windir%\$NT* /f /s /q /a:h

rem remove windows prefetch files
del c:\Windows\Prefetch\*.* /f /s /q

del /F c:\windows\system32\sysprep\panther\setupact.log
del /F c:\windows\system32\sysprep\panther\setuperr.log
del /F c:\windows\system32\sysprep\panther\ie\setupact.log
del /F c:\windows\system32\sysprep\panther\ie\setuperr.log
del /F "C:\Program Files (x86)\FOG\fog.log"
REM del /F "C:\Program Files (x86)\FOG\token.dat"

echo disabling FOGService during sysprep...
rem turn off fog service during clone
net stop FOGService
sc config FOGService start=disabled

rem run disk cleanup
echo running disk cleanup...
cleanmgr /sagerun:1


echo Do you want to zero the drive [recommended but takes hours - default N in 6 seconds]?
choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipzero
echo Writing zeros to the drive...
rem c:\apps\sdelete\sdelete -z c:
:skipzero

echo Do you want to run defrag [recommended]
choice /C yn /T 6 /D n /m "Press n for no, or y to run defrag"
if errorlevel 2 goto skipdefrag
defrag c: /U /V
:skipdefrag

REM enable the firstboot user if it exists so it can autologin
echo "enabling firstboot account..."
NET USER firstboot /active:yes

echo "Ready to sysprep"
echo "This will run sysprep and shutdown."
echo "  DO NOT do anything during sysprep!!!"
echo "  DO NOT start the machine back up - start your imaging process to capture after shutdown!!!"
echo "       hit any key to continue or CTRL+C to cancel"
pause
c:\windows\system32\sysprep\sysprep.exe /oobe /generalize /shutdown /unattend:c:\apps\sysprep_scripts\unattend.xml

