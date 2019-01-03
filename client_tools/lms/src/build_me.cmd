
set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\
rem set VCToolsRedistDir="C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Redist\MSVC\14.15.26706\"

cd build-OPE_LMS-Desktop_Qt_5_11_2_MSVC2017_64bit-Release\release

c:\Qt\5.11.2\msvc2017_64\bin\windeployqt.exe --compiler-runtime --angle OPE_LMS.exe

cd ..\..

echo Done
pause
