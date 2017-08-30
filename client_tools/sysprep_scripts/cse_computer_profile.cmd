@echo off

REM Copy profile configs to the default profile so that certain things will work.

rem oculus

xcopy /I /E /H /R /Y c:\users\huskers\appdata\roaming\oculus c:\users\default\appdata\roaming\oculus
xcopy /I /E /H /R /Y c:\users\huskers\appdata\local\oculus c:\users\default\appdata\local\oculus
xcopy /I /E /H /R /Y c:\users\huskers\appdata\roaming\oculusclient c:\users\default\appdata\roaming\oculusclient
