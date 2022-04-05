set QT_PATH=C:\Qt\6.2.4

set VC_EDITION=Community
set MSVC_VER=14.29.30133
set MSVC_MAJOR_VER=2019

rem set VC_DIR=C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC
rem set VCINSTALLDIR=C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC

rem IF NOT EXIST "%QT_PATH%\" (
rem     rem Try other QT path
rem     set QT_PATH=C:\Qt\Qt5.12.0\5.12.0
rem )


rem IF NOT EXIST "%VCINSTALLDIR%\" (
rem     rem Not pro-try enterprise
rem     set VC_EDITION=Enterprise
rem     set VCINSTALLDIR="C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC"
rem )


rem set VCToolsRedistDir="%VCINSTALLDIR%\Redist\MSVC\%MSVC_VER%\"

call "%QT_PATH%/msvc%MSVC_MAJOR_VER%_64/bin/qtenv2.bat"
call "C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC\Auxiliary\Build\vcvarsall.bat" amd64

rem cd build-OPE_LMS-Desktop_Qt_5_15_2_MSVC2019_64bit-Release\release

cd %~dp0
cd ..

set PROJECT_ROOT=%CD%
cd %~dp0

set CODE_ROOT=%PROJECT_ROOT%\OPE_LMS
rem C:\git_projects\ope\ope\client_tools\lms\src\OPE_LMS
rem %~dp0
set BUILD_DIR=%PROJECT_ROOT%\build-OPE_LMS-Desktop_Qt_6_2_4_MSVC2019_64bit-Release\release

rem set PATH=%PATH%;%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin

rem %QT_PATH%\msvc2019_64\bin\windeployqt.exe --compiler-runtime --qmldir ../../OPE_LMS --angle OPE_LMS.exe
%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin\windeployqt.exe --force --compiler-runtime --qmldir "%CODE_ROOT%" --libdir "%BUILD_DIR%" --dir "%BUILD_DIR%" "%BUILD_DIR%\OPE_LMS.exe"


REM NOTE - Need to move resources/* to release folder
rem xcopy /YI "%BUILD_DIR%/plugins/resources" "%BUILD_DIR%/resources"
REM NOTE - Need to move translations/qtwebengine_locales to release folder
xcopy /YI "%BUILD_DIR%/translations/qtwebengine_locales" "%BUILD_DIR%/i18n/qtwebengine_locales"
rem echo "%BUILD_DIR%\plugins\QtWebEngineProcess.exe"
rem copy /Y "%BUILD_DIR%\plugins\QtWebEngineProcess.exe" "%BUILD_DIR%\"

REM Stupid windeployqt - need plugins NOT in plugin folder, except TLS
xcopy /YI "%BUILD_DIR%\tls" "%BUILD_DIR%\plugins\tls"

rem Move back to project folder
rem cd ..\..\OPE_LMS

echo Done Building!!!!
pause
