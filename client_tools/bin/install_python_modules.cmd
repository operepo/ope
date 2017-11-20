@echo off

set PIP=c:\python27\python.exe -m pip

echo Installing modules from list...

powershell -Command "%PIP% install --no-cache-dir -r python_module_list.txt "

echo Done.
pause