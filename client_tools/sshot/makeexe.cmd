REM Python2

cd %~dp0

python2 build.py

REM Old build using py2exe, using pyinstaller
REM python setup.py py2exe

rem xcopy /Y /E dist\* ..\update\

echo "Build complete"
pause
