@echo off

REM Make sure we are in the root project folder
cd %~dp0
cd ..

echo Killing OPE_LMS app if running...
taskkill /f /im OPE_LMS.exe   1>NUL 2>NUL

echo Updating OPE Code from SMC Server...
bin\bin\git.exe remote remove ope_smc_origin
bin\bin\git.exe remote add ope_smc_origin git://smc.ed/ope_laptop_binaries.git
bin\bin\git.exe pull ope_smc_origin master

if "%1" NEQ "auto" (
    echo Git pull finished!
    pause
)
