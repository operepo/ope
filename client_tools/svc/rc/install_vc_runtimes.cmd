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

rem Install each MSVC if it isn't installed

rem ---- MSVC 2005 ----
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\84b9c17023c712640acaf308593282f8
set MSVC_VERSION=MSVC 2005 x64
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x64_2005.exe /q
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)

set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\b25099274a207264182f8181add555d0
set MSVC_VERSION=MSVC 2005 x86
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x86_2005.exe /q
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)




rem ---- MSVC 2008 ----
REM 67D6ECF5CD5FBA732B8B22BAC8DE1B4D - Microsoft Visual C++ 2008 Redistributable - x64 9.0.30729.6161
REM 1007C6B46D7C017319E3B52CF3EC196E - Microsoft Visual C++ 2008 Redistributable - x64 9.0.30729.4148
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\67D6ECF5CD5FBA732B8B22BAC8DE1B4D
set MSVC_VERSION=MSVC 2008 x64
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x64_2008.exe /q
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)
REM 6E815EB96CCE9A53884E7857C57002F0 - Microsoft Visual C++ 2008 Redistributable - x86 9.0.30729.6161
REM CFD2C1F142D260E3CB8B271543DA9F98 - Microsoft Visual C++ 2008 Redistributable - x86 9.0.30729.4148
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\6E815EB96CCE9A53884E7857C57002F0
set MSVC_VERSION=MSVC 2008 x86
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x86_2008.exe /q
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)


rem ---- MSVC 2010 ----
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\1926E8D15D0BCE53481466615F760A7F
set MSVC_VERSION=MSVC 2010 x64
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x64_2010.exe /q /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)

set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\1D5E3C0FEDA1E123187686FED06E995A
set MSVC_VERSION=MSVC 2010 x86
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x86_2010.exe /q /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)



rem ---- MSVC 2012 ----
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\C3AEB2FCAE628F23AAB933F1E743AB79
rem F90E4FA5B9C5FAA37B1345D4D38C12DD
set MSVC_VERSION=MSVC 2012 x64
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x64_2012.exe /install /quiet /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)

set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\DC8A59DBF9D1DA5389A1E3975220E6BB
set MSVC_VERSION=MSVC 2012 x86
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x86_2012.exe /install /quiet /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)




rem ---- MSVC 2013 ----
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\4BB91BBAD8382803DB4A786C0614182A
rem CE6380BC270BD863282B3D74B09F7570
set MSVC_VERSION=MSVC 2013 x64
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x64_2013.exe /install /quiet /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)

set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\3E8F7AED9B7BC3C349B5F7C89E407184
rem 21EE4A31AE32173319EEFE3BD6FDFFE3
set MSVC_VERSION=MSVC 2013 x86
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vcredist_x86_2013.exe /install /quiet /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)



rem ---- MSVC 2015-2019 ----
set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\4891423FE0A523640952AA610E87A0B4
set MSVC_VERSION=MSVC 2015-2019 x64
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vc_redist.x64_15_to_19.exe /install /quiet /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)

set REG_KEY=HKLM\SOFTWARE\Classes\Installer\Products\1AF6F69BF0351F24F917335C38173604
set MSVC_VERSION=MSVC 2015-2019 x86
set MSG=%ESC_GREEN%---- Checking install of !MSVC_VERSION!... ----%ESC_RESET%
echo !MSG!
reg query "!REG_KEY!" >> nul 2>&1
if %ERRORLEVEL% NEQ 0 (
 echo %ESC_RED%    - !MSVC_VERSION! not installed, installing now...%ESC_RESET%
 call %~dp0vc_redist.x86_15_to_19.exe /install /quiet /norestart
) else (
 echo %ESC_GREEN%    - !MSVC_VERSION! already installed.%ESC_RESET%
)




rem Shouldn't need this - dlls should be located in the app folder
rem NOTE - As of 5/16/19 - qt still needing 1.0.? Open ssl version
rem call %~dp0Win64OpenSSL_Light-1_1_1b.exe /silent /allusers /nocancel /norestart /closeapplications /restartapplications /noicons
rem  /verysilent
