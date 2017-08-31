REM Create SetupComplete.cmd (C:\Windows\Setup\Scripts\SetupComplete.cmd)

rem disable ipv6 - interferes w joining domains in some cases - set back to 0 to enable (windows default)
reg add HKLM\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters /v DisabledComponents /t REG_DWORD /d 0xff /f

rem make sure we don't have hibernate enabled
powercfg /H off

rem disable firstboot user after done
rem NET USER firstboot /active:no

rem reboot
rem NOTE NOTE NOTE - if this runs as a proper SetupComplete script, don't reboot here!
rem if it runs as a user startup script, then reboot should be ok
rem if NOT "%1%"=="reboot" goto skipreboot
	rem echo "Rebooting..."
rem	shutdown /r /t 1
rem :skipreboot

rem make sure fog service is enabled
sc config FOGService start=delayed-auto
net start FOGService