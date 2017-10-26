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



rem activate windows with KMS server
rem install public key
rem win 10 enterprise - NPPR9-FWDCX-D2C8J-H872K-2YT43
c:\windows\system32\slmgr.vbs /ipk NPPR9-FWDCX-D2C8J-H872K-2YT43
rem activate with kms server
c:\windows\system32\slmgr.vbs /ato
rem view detailed info
rem slmgr.vbs /dlv

rem enable auto discovery of kms server
rem slmgr.vbs /ckms
rem manual activation
rem slmgr.vbs /skms server:port

rem activate office 2016 with KMS server
rem CD \Program Files\Microsoft Office\Office16
rem specify server name
rem cscript ospp.vbs /sethst:kms01.yourdomain.com
rem activate office 
cscript c:\Program Files\Microsoft Office\Office16ospp.vbs /act
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


rem make sure fog service is enabled
sc config FOGService start=delayed-auto
net start FOGService
