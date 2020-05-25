@echo off

rem escape code for colors
SET ESC=[
SET ESC_CLEAR=%ESC%2j
SET ESC_RESET=%ESC%0m
SET ESC_GREEN=%ESC%32m
SET ESC_RED=%ESC%31m
SET ESC_YELLOW=%ESC%33m


:instgpo

cd %~dp0

echo %ESC_GREEN%Restoring local GPO settings...%ESC_RESET%
%~dp0lgpo.exe /g "%~dp0rc\gpo" 
echo %ERRORLEVEL%
if %ERRORLEVEL% == 0 (
    echo %ESC_GREEN%success!%ESC_RESET%
) else (
    echo.
    echo. 
    echo %ESC_RED%===== Error applying gpo settings!!! =====%ESC_RESET%
    echo.
    echo.
    echo %ESC_YELLOW% It is VERY important that this completes to secure the laptop!!! %ESC_RESET%
    echo.
    choice /C y /T 3 /D y /M " Do you want to try again? (yes you have to complete this to secure the laptop!!!!)"
    rem if errorlevel 2 goto endcredential
    
    goto instgpo
)

rem 2>NUL 1<NUL


%windir%\system32\gpupdate /force 