@echo off


rem https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/bcdedit--set


echo Setting boot timeout to 0
bcdedit /timeout 0

rem Use standard policy - no F8 key
bcdedit /set {current} bootmenupolicy Standard

rem Try to boot normally every time - helps to not show recovery options
echo Ignoring all boot errors
bcdedit /set {current} bootstatuspolicy ignoreallfailures

echo Disabling Automatic Recovery
bcdedit /set {current} recoveryenabled No


