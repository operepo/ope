REM  After reboot (TWICE!!!) run this script to sysprep
@echo off
delprof2 /q /id:firstboot /i
NET USER firstboot /DELETE
powercfg -h off
rem C:\Support\Tools\Shutup\OOSU10.exe ooshutup10.cfg /quiet
del /F c:\windows\system32\sysprep\panther\setupact.log
del /F c:\windows\system32\sysprep\panther\setuperr.log
del /F c:\windows\system32\sysprep\panther\ie\setupact.log
del /F c:\windows\system32\sysprep\panther\ie\setuperr.log
del /F "C:\Program Files (x86)\FOG\fog.log"
REM del /F "C:\Program Files (x86)\FOG\token.dat"
rem "C:\Program Files\Oracle\VirtualBox Guest Additions\uninst.exe"
mkdir C:\Windows\Setup\scripts
copy SetupComplete.cmd C:\Windows\Setup\scripts\ /Y
copy unattend.xml C:\Windows\System32\Sysprep /Y
rem reg import C:\Support\Tools\ResetERAgentUUID.reg
net stop FOGService
sc config FOGService start=disabled
REM sc config EraAgentSvc start=disabled
cleanmgr /sagerun:1
REM defrag c:
echo "Ready to sysprep - hit any key to continue or CTRL+C to cancel"
pause
c:\windows\system32\sysprep\sysprep.exe /oobe /generalize /shutdown /unattend:c:\windows\system32\sysprep\unattend.xml

