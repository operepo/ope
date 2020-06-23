@echo off
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

rem escape code for colors
SET ESC=[
SET ESC_CLEAR=%ESC%2j
SET ESC_RESET=%ESC%0m
SET ESC_GREEN=%ESC%32m
SET ESC_RED=%ESC%31m
SET ESC_YELLOW=%ESC%33m



rem need to copy the OPEService folder into the proper location

echo %ESC_GREEN%Copying latest version of Services to ope_laptop_binaries...%ESC_RESET%
rem /Q for quiet, /F for full
SET QUIET_FLAG=/Q

if exist OPEService.py (
    rem Make sure to remove extra gpo stuff before copy so we don't end up with 2
    echo -- Clearing old GPO files %~dp0\..\..\..\ope_laptop_binaries\Services\mgmt\rc\gpo
    rmdir /S /Q %~dp0\..\..\..\ope_laptop_binaries\Services\mgmt\rc\gpo
    rem /Q instead of F
    echo -- Copying %~dp0\dist\ to %~dp0\..\..\..\ope_laptop_binaries\Services\
    xcopy /ECIHRKY %QUIET_FLAG% %~dp0\dist\* %~dp0\..\..\..\ope_laptop_binaries\Services\ 
) else (
    rem echo -- Copying %~dp0\dist\ to %programdata%\ope\Services\
    rem xcopy /ECIHRKY %QUIET_FLAG% %~dp0\..\Services\* %programdata%\ope\Services\
)

echo Done!