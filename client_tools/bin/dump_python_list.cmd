@echo off

set PIP=c:\python27\python.exe -m pip

echo Dumping list...

powershell -Command "%PIP% list --format=freeze | %%{ echo \"$_\" } " > python_module_list.txt

echo Done.
pause