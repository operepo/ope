@echo off

echo %%~dp0 is "%~dp0"
echo %%0 is "%0"
echo %%~dpnx0 is "%~dpnx0"
echo %%~f1 is "%~f1"
echo %%~dp0%%~1 is "%~dp0%~1"

set upath=%~dp0unattend.xml
echo %upath%

echo done
pause