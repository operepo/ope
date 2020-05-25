@echo off

cd %~dp0


rem reset secpol.msc settings to default (admin settings)
cd %windir%\system32
secedit /configure /cfg %windir%\inf\defltbase.inf /db defltbase.sdb /verbose 2>NUL 1<NUL


rem remove current group policy objects
rd /S /Q "%windir%\System32\GroupPolicyUsers" 2>NUL 1<NUL
rd /S /Q "%windir%\System32\GroupPolicy" 2>NUL 1<NUL

gpupdate /force 2>NUL 1<NUL


