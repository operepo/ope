@echo off

rem escape code for colors
SET ESC=[
SET ESC_CLEAR=%ESC%2j
SET ESC_RESET=%ESC%0m
SET ESC_GREEN=%ESC%32m
SET ESC_RED=%ESC%31m
SET ESC_YELLOW=%ESC%33m

rem download and install the certs
echo %ESC_GREEN%Downloading Fog certs...%ESC_RESET%


%~dp0wget.exe --connect-timeout=6 --tries=3 --no-check-certificate -O %~dp0ca.crt https://gateway.ed/ca.crt  2>NUL 1>NUL

if %ERRORLEVEL% == 0 (
    echo %ESC_GREEN%  Certs downloaded!%ESC_RESET%
) else (
    echo.
    echo. 
    echo %ESC_RED%===== Error downloading OPE Certs!!! =====%ESC_RESET%
    echo.
    echo.
    pause
)

rem install the certs
echo %ESC_GREEN%    Installing OPE certs...%ESC_RESET%

REM remove old certs
rem %~dp0certmgr.exe -del -c -n "ed" -s -r localMachine Root

REM add current cert
%~dp0certmgr.exe -add %~dp0ca.crt  -c -s -r localMachine root  2>NUL 1>NUL

if %ERRORLEVEL% == 0 (
    echo %ESC_GREEN%  Success! OPE Certs installed%ESC_RESET%
) else (
    echo.
    echo. 
    echo %ESC_RED%===== Error installing OPE Certs!!! =====%ESC_RESET%
    echo.
    echo.
    pause
)


