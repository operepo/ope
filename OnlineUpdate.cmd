rem @echo off
cd %~dp0
echo %~dp0

echo Updating OPE Code...
%~dp0\bin\bin\git.exe remote remove ope_origin
%~dp0\bin\bin\git.exe remote add ope_origin https://github.com/operepo/ope.git
%~dp0\bin\bin\git.exe pull ope_origin master

echo Update finished!
pause
