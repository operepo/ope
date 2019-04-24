REM - Python2
call remove_service.cmd
python2 setup.py py2exe

rem xcopy /Y /E dist\* ..\update\

echo "Build complete"
pause
