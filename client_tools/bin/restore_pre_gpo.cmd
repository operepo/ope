@echo off

cd %~dp0

echo Restoring local GPO settings...
echo gpo_path %~dp0rc\pre_gpo
%~dp0lgpo.exe /g "%~dp0rc\pre_gpo"


%windir%\system32\gpupdate /force