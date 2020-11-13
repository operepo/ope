cd ..

rem Home - c:\Qt\5.12.0, school - C:\Qt\Qt5.12.0\5.12.0
rem set QT_PATH=C:\Qt\Qt5.12.0\5.12.0
set QT_PATH=C:\Qt\5.15.1

rem Home - Professional, School - Enterprise
rem set VC_EDITION=Professional
set VC_EDITION=Community
rem MSVC_VER=14.16.27023
set MSVC_VER=14.27.29110
set MSVC_MAJOR_VER=2019

set VC_DIR=C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC
set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC

IF NOT EXIST "%QT_PATH%\" (
    rem Try other QT path
    set QT_PATH=C:\Qt\Qt5.12.0\5.12.0
)




IF NOT EXIST "%VCINSTALLDIR%\" (
    rem Not pro-try enterprise
    set VC_EDITION=Enterprise
    set VCINSTALLDIR="C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC"
)


set VCToolsRedistDir="%VCINSTALLDIR%\Redist\MSVC\%MSVC_VER%\"

cd build-OPE_LMS-Desktop_Qt_5_15_1_MSVC2019_64bit-Release\release

%QT_PATH%\msvc2019_64\bin\windeployqt.exe --compiler-runtime --qmldir ../../OPE_LMS --angle OPE_LMS.exe


REM NOTE - Need to move resources/* to release folder
xcopy /YI resources .
REM NOTE - Need to move translations/qtwebengine_locales to release folder
xcopy /YI "translations/qtwebengine_locales" "./qtwebengine_locales"

rem Move back to project folder
cd ..\..\OPE_LMS

echo Done Building!!!!
pause
