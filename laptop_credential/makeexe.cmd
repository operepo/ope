
cd %~dp0
rem Use pyinstaller build, not old py2exe build
rem python2 build.py
python build.py

REM python2 setup.py py2exe

rem xcopy /Y /E dist\* ..\update\

echo "Build complete"
echo "Copy dist files to binary folder and commit/push with git to publish."
pause
