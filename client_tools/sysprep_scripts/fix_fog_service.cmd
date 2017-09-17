@echo off

rem download and install the certs for the fog service
echo Downloading certs...
wget -O srvpublic.crt http://fog.ed/fog/management/other/ssl/srvpublic.crt
wget -O ca.cert.der http://fog.ed/fog/management/other/ca.cert.der

rem install the certs
echo Installing certs...
certmgr.exe -add ca.cert.der -c -s -r localMachine root
rem certmgr.exe -add ca.cert.der -c -s -r localMachine trustedpublisher
certmgr.exe -add srvpublic.crt -c -s -r localMachine root
rem certmgr.exe -add srvpublic.crt -c -s -r localMachine trustedpublisher

rem restart the fogservice
echo Restarting FogService
net stop fogservice
net start fogservice
