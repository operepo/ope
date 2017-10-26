REM  SEE setupcomplete script for commands TODO TODO TODO
exit

REM OEM KEY FROM BIOS - need oemkey.exe
@echo off
for /f "tokens=*" %%i in ('%cd%\oemkey') do set oemkey=%%i
cscript %systemroot%\system32\slmgr.vbs /ipk %oemkey% >nul
cscript %systemroot%\system32\slmgr.vbs /ato >nul
exit
