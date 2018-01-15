@echo off
cd %~dp0

echo Updating OPE Code from SMC Server...
%~dp0\bin\bin\git.exe remote remove ope_smc_origin
%~dp0\bin\bin\git.exe remote add ope_smc_origin git://smc.ed/ope.git
%~dp0\bin\bin\git.exe pull ope_smc_origin master

echo Update finished!
pause
