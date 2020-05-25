rem @echo off

REM Make sure we are in project root folder
cd %~dp0
cd ..

echo Updating OPE Code...
bin\bin\git.exe remote remove ope_origin
bin\bin\git.exe remote add ope_origin https://github.com/operepo/ope_laptop_binaries.git
bin\bin\git.exe pull ope_origin master

if "%1" NEQ "auto" (
    echo Git pull finished!
    pause
)