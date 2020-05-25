@echo off

cd %~dp0

REM Remove old stuff
rd /q /s gpo_tmp

mkdir gpo_tmp


echo Dumping local GPO settings to gpo_tmp...
%~dp0\lgpo.exe /b "%~dp0\gpo_tmp"

