@echo off

net stop OPEService >> nul 2>&1

rem Service should always be in the programdata\ope\OPEService folder
%programdata%\ope\Services\OPEService\OPEService.exe remove


goto endofscript


:endofscript
