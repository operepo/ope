@echo off

set QT_VER=6.8.0
set QT_VER_FOLDER=6_8_0

set QT_PATH=C:\Qt\%QT_VER%

set VC_EDITION=Community
set MSVC_VER=14.41.34120
set MSVC_MAJOR_VER=2022
set PROGRAM_FILES=Program Files
rem C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.41.34120\include

rem WORKAROUND - qt 6.5 fails on windeployqt - should be fixed in 6.5.1
set TRANSLATIONS=--no-translations

rem set MSVC_BINARIES=C:\%PROGRAM_FILES%\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC\Redist\MSVC\%MSVC_VER%\x64\Microsoft.VC142.CRT
rem set MSVC_BINARIES=C:\%PROGRAM_FILES%\Microsoft Visual Studio\%MSVC_MAJOR_VER%\Community\VC\Redist\MSVC\%MSVC_VER%\x64\Microsoft.VC143.CRT
set MSVC_BINARIES=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Redist\MSVC\14.40.33807\x64\Microsoft.VC143.CRT
rem C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Redist\MSVC\14.40.33807

rem set VCToolsRedistDir="%VCINSTALLDIR%\Redist\MSVC\%MSVC_VER%\"
rem echo QT ENV - %QT_ENV_SETUP%
if "%QT_ENV_SETUP%" NEQ "1" (
    call "%QT_PATH%/msvc%MSVC_MAJOR_VER%_64/bin/qtenv2.bat"
    rem call "C:\%PROGRAM_FILES%\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC\Auxiliary\Build\vcvarsall.bat" x64
    call "C:\%PROGRAM_FILES%\Microsoft Visual Studio\%MSVC_MAJOR_VER%\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    set QT_ENV_SETUP=1
    rem echo "SET ENV"
)

echo Building...
rem cd build-OPE_LMS-Desktop_Qt_5_15_2_MSVC2019_64bit-Release\release

cd %~dp0
cd ..

set PROJECT_ROOT=%CD%
cd %~dp0

set CODE_ROOT=%PROJECT_ROOT%\OPE_LMS
rem C:\git_projects\ope\ope\client_tools\lms\src\OPE_LMS
rem %~dp0
rem set RELEASE_BUILD_DIR=%PROJECT_ROOT%\build-OPE_LMS-Desktop_Qt_%QT_VER_FOLDER%_MSVC%MSVC_MAJOR_VER%_64bit-Release\release
rem set DEBUG_BUILD_DIR=%PROJECT_ROOT%\build-OPE_LMS-Desktop_Qt_%QT_VER_FOLDER%_MSVC%MSVC_MAJOR_VER%_64bit-Debug\debug
set RELEASE_BUILD_DIR=%CODE_ROOT%\build\Desktop_Qt_%QT_VER_FOLDER%_MSVC%MSVC_MAJOR_VER%_64bit-Release\release
set DEBUG_BUILD_DIR=%CODE_ROOT%\build\Desktop_Qt_%QT_VER_FOLDER%_MSVC%MSVC_MAJOR_VER%_64bit-Debug\debug

rem set PATH=%PATH%;%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin

rem %QT_PATH%\msvc2019_64\bin\windeployqt.exe --compiler-runtime --qmldir ../../OPE_LMS --angle OPE_LMS.exe
%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin\windeployqt.exe %TRANSLATIONS% --force --compiler-runtime --qmldir "%CODE_ROOT%" --libdir "%RELEASE_BUILD_DIR%" --dir "%RELEASE_BUILD_DIR%" --plugindir "%RELEASE_BUILD_DIR%\plugins" "%RELEASE_BUILD_DIR%\OPE_LMS.exe"

%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin\windeployqt.exe %TRANSLATIONS% --force --compiler-runtime --qmldir "%CODE_ROOT%" --libdir "%DEBUG_BUILD_DIR%" --dir "%DEBUG_BUILD_DIR%" --plugindir "%DEBUG_BUILD_DIR%\plugins" "%DEBUG_BUILD_DIR%\OPE_LMS.exe"


REM NOTE - Need to move resources/* to release folder
rem xcopy /YI "%BUILD_DIR%/plugins/resources" "%BUILD_DIR%/resources"
REM NOTE - Need to move translations/qtwebengine_locales to release folder
rem xcopy /YI "%RELEASE_BUILD_DIR%/translations/qtwebengine_locales" "%RELEASE_BUILD_DIR%/i18n/qtwebengine_locales"
rem xcopy /YI "%DEBUG_BUILD_DIR%/translations/qtwebengine_locales" "%DEBUG_BUILD_DIR%/i18n/qtwebengine_locales"
rem echo "%BUILD_DIR%\plugins\QtWebEngineProcess.exe"
rem copy /Y "%BUILD_DIR%\plugins\QtWebEngineProcess.exe" "%BUILD_DIR%\"

REM Stupid windeployqt - need plugins NOT in plugin folder, except TLS
rem xcopy /YI "%RELEASE_BUILD_DIR%\tls" "%RELEASE_BUILD_DIR%\plugins\tls"
rem xcopy /YI "%DEBUG_BUILD_DIR%\tls" "%DEBUG_BUILD_DIR%\plugins\tls"

rem Move back to project folder
rem cd ..\..\OPE_LMS

Rem Copy in MSVC run time files
rem concrt140.dll, msvcp140.dll, vccorlib140.dll, and vcruntime140.dll.
echo "Copying MSVC Binaries from %MSVC_BINARIES% to %RELEASE_BUILD_DIR%"
xcopy /YI "%MSVC_BINARIES%\*" "%RELEASE_BUILD_DIR%"
echo "Copying MSVC Binaries from %MSVC_BINARIES% to %DEBUG_BUILD_DIR%"
xcopy /YI "%MSVC_BINARIES%\*" "%DEBUG_BUILD_DIR%"

echo Done Building!!!!
pause
