REM  After reboot (TWICE!!! for chkdsk to finish?) run this script to sysprep
@echo off

echo Turn off hibernate...
powercfg /H off

rem remove firstboot profile
REM echo removing firstboot profile...
REM wmic /node:localhost path win32_UserProfile where LocalPath="c:\\users\\firstboot" Delete 2>>c:\apps\sysprep_scripts\wmic.err

rem delete shadow copies
echo deleting shadow copies...
vssadmin delete shadows /All /Quiet

rem Delete hidden win install files
rem echo clearing win install files...
rem del %windir%\$NT* /f /s /q /a:h

rem remove windows prefetch files
rem del c:\Windows\Prefetch\*.* /f /s /q

del /F c:\windows\system32\sysprep\panther\setupact.log
del /F c:\windows\system32\sysprep\panther\setuperr.log
del /F c:\windows\system32\sysprep\panther\ie\setupact.log
del /F c:\windows\system32\sysprep\panther\ie\setuperr.log
del /F "C:\Program Files (x86)\FOG\fog.log"
del /F "C:\Program Files (x86)\FOG\token.dat"

echo disabling FOGService during sysprep...
rem turn off fog service during clone
net stop FOGService
sc config FOGService start=disabled

echo Do you want to run disk cleanup [recommended - default Y in 6 seconds]?
choice /C yn /T 6 /D y /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipdiskcleanup
echo running disk cleanup...
cleanmgr /sagerun:1
:skipdiskcleanup


echo Do you want to zero the drive [recommended but takes hours - default N in 6 seconds]?
choice /C yn /T 6 /D n /M "Press y for yes, or n to skip"
if errorlevel 2 goto skipzero
echo Writing zeros to the drive...
rem c:\apps\sdelete\sdelete -z c:
:skipzero

echo Do you want to run defrag [recommended]?
choice /C yn /T 6 /D n /m "Press n for no, or y to run defrag"
if errorlevel 2 goto skipdefrag
defrag c: /U /V
:skipdefrag

REM enable the firstboot user if it exists so it can autologin
echo "enabling firstboot account..."
NET USER firstboot /active:yes

echo "This will run sysprep and shutdown."
echo Do you want to run sysprep [recommended]?
choice /C yn /m "Press n for no, or y to run sysprep"
if errorlevel 2 goto skipsysprep
echo "  DO NOT do anything during sysprep!!!"
echo "  DO NOT start the machine back up - start your imaging process to capture after shutdown!!!"
rem get current path for the unattend.xml file
set upath=%~dp0unattend.xml
c:\windows\system32\sysprep\sysprep.exe /oobe /generalize /shutdown /unattend:%upath%
:skipsysprep
