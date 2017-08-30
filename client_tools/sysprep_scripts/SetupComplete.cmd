REM Create SetupComplete.cmd (C:\Windows\Setup\Scripts\SetupComplete.cmd)

rem make sure fog service is enabled
sc config FOGService start=delayed-auto
net start FOGService

rem make sure we don't have hibernate enabled
powercfg /H off

rem disable firstboot user after done
NET USER firstboot /active:no

rem reboot
rem NOTE NOTE NOTE - if this runs as a proper SetupComplete script, don't reboot here!
rem if it runs as a user startup script, then reboot should be ok
rem shutdown /r /t 1