@echo off

set PIP=c:\python27\python.exe -m pip

echo Updating python modules...

powershell -Command "%PIP% list --outdated --format=freeze | %%{$_.split('==')[0]} | %%{ If(-NOT ($_ -eq 'CairoSVG')){ %PIP% install --upgrade $_ } Else { echo \"   Skipping $_...\" } }"

echo Upgrade complete.
pause