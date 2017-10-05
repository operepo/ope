@echo off

rem get current folder
set curr_dir=%~dp0

echo %curr_dir%

mkdir gpo
echo Backing up current local GPO settings...
lgpo.exe /b "%curr_dir%gpo" /n ope_gpo

