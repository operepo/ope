@echo off

rem get current folder
set curr_dir=%~dp0

echo %curr_dir%

rem mkdir gpo
echo Restoring local GPO settings...
lgpo.exe /g "%curr_dir%gpo"


