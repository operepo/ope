REM Create SetupComplete.cmd (C:\Windows\Setup\Scripts\SetupComplete.cmd)

rem del C:\Windows\System32\Sysprep\unattend.xml
sc config FOGService start=delayed-auto
net start FOGService
powercfg /H off
rem del C:\Windows\Setup\Scripts\SetupComplete.cmd
