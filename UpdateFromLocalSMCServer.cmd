@echo off

echo Updating OPE Code from SMC Server...
PortableGit\bin\git.exe remote remove ope_smc_origin
PortableGit\bin\git.exe remote add ope_smc_origin git://smc.ed/ope.git
PortableGit\bin\git.exe pull ope_smc_origin master

echo Update finished!
pause
