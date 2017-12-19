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
rem echo clearing win install files...
rem del %windir%\$NT* /f /s /q /a:h

rem remove windows prefetch files
rem del c:\Windows\Prefetch\*.* /f /s /q

del /F c:\windows\system32\sysprep\panther\setupact.log
del /F c:\windows\system32\sysprep\panther\setuperr.log
del /F c:\windows\system32\sysprep\panther\ie\setupact.log
del /F c:\windows\system32\sysprep\panther\ie\setuperr.log

echo disabling FOGService during sysprep...
rem turn off fog service during clone
net stop FOGService
sc config FOGService start=disabled

del /F "C:\Program Files (x86)\FOG\fog.log"
del /F "C:\fog.log"
del /F "C:\Program Files (x86)\FOG\token.dat"


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
rem c:\windows\setup\sysprep_scripts\sdelete\sdelete -z c:
:skipzero

echo Do you want to run defrag [recommended]?
choice /C yn /T 6 /D n /m "Press n for no, or y to run defrag"
if errorlevel 2 goto skipdefrag
defrag c: /U /V
:skipdefrag

REM enable the firstboot user if it exists so it can autologin
rem echo "enabling firstboot account..."
rem NET USER firstboot /active:yes
rem set startup script
rem wmic /node:localhost path win32_NetworkLoginProfile where caption="firstboot" set scriptpath="c:\apps\sysprep_scripts\SetupComplete.cmd"
REM NOTE: This will run for ANY user that logs in, so the firstboot user doesn't need a startup script, just be set to login.
rem reg add HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce /v SetupComplete /t REG_SZ /d "c:\apps\sysprep_scripts\SetupComplete.cmd reboot" /f
rem reg add HKLM\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce /v SetupComplete /t REG_SZ /d "c:\apps\sysprep_scripts\SetupComplete.cmd" /f

rem disable cortana
rem reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f


rem Export current app defaults so we can import them later
DISM /online /export-defaultappassociations:AppAssoc.xml

REM PC software - use these keys for win 10 pro and office 2016
REM cscript c:\windows\system32\slmgr.vbs /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX
REM cscript 'c:\Program Files\Microsoft Office\Office16\ospp.vbs' /inpkey:XQNVK-8JYDB-WJ9W3-YJ8YR-WFG99

REM ---------- SCRATCH -------------------
rem activate windows with KMS server
rem install public key
rem win 10 pro - W269N-WFGWX-YVC9B-4J6C9-T83GX
rem win 10 enterprise - NPPR9-FWDCX-D2C8J-H872K-2YT43
REM c:\windows\system32\slmgr.vbs /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX
rem activate with kms server
REM c:\windows\system32\slmgr.vbs /ato
rem view detailed info
rem slmgr.vbs /dlv

rem enable auto discovery of kms server
rem slmgr.vbs /ckms
rem manual activation
rem slmgr.vbs /skms server:port


REM set APP=sysinternalssuite\psexec.exe
REM set LIST=computer_list_test.txt
REM set LIST=computer_list.txt

REM active win 10
REM %APP% @%LIST% -dehs cmd /C "cscript 'c:\windows\system32\slmgr.vbs' /ipk W269N-WFGWX-YVC9B-4J6C9-T83GX"
REM %APP% @%LIST% -dehs cmd /C "cscript 'c:\windows\system32\slmgr.vbs' /ato"


REM activate office
REM %APP% @%LIST% -dehs cmd /C "cscript 'c:\Program Files\Microsoft Office\Office16\ospp.vbs' /inpkey:XQNVK-8JYDB-WJ9W3-YJ8YR-WFG99"
REM %APP% @%LIST% -dehs cmd /C "cscript 'c:\Program Files\Microsoft Office\Office16\ospp.vbs' /act"


rem activate office 2016 with KMS server
rem CD \Program Files\Microsoft Office\Office16
rem specify server name
rem cscript ospp.vbs /sethst:kms01.yourdomain.com
REM set public kms key for office 2016
rem .\psexec.exe \\acct-inst,acct-1,acct-2,acct-3,acct-4,acct-5,acct-ta1,acct-ta2 -u huskers -dehs cmd /C "cscript 'c:\Program Files\Microsoft Office\Office16\ospp.vbs' /inpkey:XQNVK-8JYDB-WJ9W3-YJ8YR-WFG99"
rem activate office 
REM REM cscript c:\Program Files\Microsoft Office\Office16\ospp.vbs /act
rem status of activation 
rem cscript ospp.vbs /dstatusall
rem disable host cache
rem cscript ospp.vbs /cachst:FALSE
rem enable host cache
rem cscript ospp.vbs /cachst:TRUE

rem --- kms notes - activate kms host - activate initial host requires internet or phone ---
rem Check current status
rem slmgr.vbs /dlv
rem uninstall current kms key
rem slmgr.vbs /upk
rem install new KMS key
rem slmgr.vbs /ipk KEY TO INSTALL
rem activate kms host
rem slmgr.vbs /ato
rem c:\windows\system32\slmgr.vbs
REM ---------- SCRATCH -------------------

rem allow win store apps to update again
REM reg delete HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\WindowsStore /v AutoDownload /f


REM Copy SetupComplete.cmd to c:\windows\setup\scripts\
c:\windows\system32\takeown.exe /f ..\Scripts
c:\windows\system32\icacls.exe ..\Scripts /grant Administrators:(OI)(CI)F /T
copy %~dp0\SetupComplete.cmd c:\windows\setup\scripts\

echo -----------------------------------------------------------------
echo - NOTE - broken win 10 1709 - will fail on sysprep
echo - Edit c:\windows\system32\sysprep\actionscripts\generalize.xml
echo - Comment out whole section on Appx (from <image to </image> )
echo -----------------------------------------------------------------
echo
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
