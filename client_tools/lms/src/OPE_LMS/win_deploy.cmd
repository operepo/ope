cd ..

rem Home - c:\Qt\5.12.0, school - C:\Qt\Qt5.12.0\5.12.0
rem set QT_PATH=C:\Qt\Qt5.12.0\5.12.0
set QT_PATH=C:\Qt\5.12.0

IF NOT EXIST "%QT_PATH%\" (
    rem Try other QT path
    set QT_PATH=C:\Qt\Qt5.12.0\5.12.0
)

rem Home - Professional, School - Enterprise
set VC_EDITION=Professional
set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\2017\%VC_EDITION%\VC

IF NOT EXIST "%VCINSTALLDIR%\" (
    rem Not pro-try enterprise
    set VC_EDITION=Enterprise
    set VCINSTALLDIR="C:\Program Files (x86)\Microsoft Visual Studio\2017\%VC_EDITION%\VC"
)


set VCToolsRedistDir="%VCINSTALLDIR%\Redist\MSVC\14.15.26706\"

cd build-OPE_LMS-Desktop_Qt_5_12_0_MSVC2017_64bit-Release\release

%QT_PATH%\msvc2017_64\bin\windeployqt.exe --compiler-runtime --qmldir ../../OPE_LMS --angle OPE_LMS.exe


REM NOTE - Need to move resources/* to release folder
xcopy /YI resources .
REM NOTE - Need to move translations/qtwebengine_locales to release folder
xcopy /YI "translations/qtwebengine_locales" "./qtwebengine_locales"

rem Move back to project folder
cd ..\..\OPE_LMS

echo Done Building!!!!
pause
