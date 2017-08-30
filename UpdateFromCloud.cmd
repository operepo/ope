@echo off

echo Updating OPE Code...
PortableGit\bin\git.exe remote remove ope_origin
PortableGit\bin\git.exe remote add ope_origin https://github.com/operepo/ope.git
PortableGit\bin\git.exe pull ope_origin master

echo Update finished!
pause
