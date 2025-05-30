@echo off
setlocal EnableDelayedExpansion

:: Qt and Visual Studio settings
set QT_VER=6.8.3
set QT_VER_FOLDER=6_8_3
set QT_PATH=C:\Qt\%QT_VER%
set VC_EDITION=Community
set MSVC_VER=14.44.35207
set MSVC_MAJOR_VER=2022
set PROGRAM_FILES=Program Files

:: Get project root dynamically using git
for /f %%i in ('git rev-parse --show-toplevel') do set PROJECT_ROOT=%%i
if errorlevel 1 (
    :: Fallback to script location if not in git repo
    set PROJECT_ROOT=%~dp0..
)

:: Set build type from argument or default to both
set BUILD_TYPE=%1
if "%BUILD_TYPE%"=="" set BUILD_TYPE=both
if not "%BUILD_TYPE%"=="debug" if not "%BUILD_TYPE%"=="release" if not "%BUILD_TYPE%"=="both" (
    echo Invalid build type. Use: debug, release, or both
    exit /b 1
)

:: Setup paths
set MSVC_BINARIES=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Redist\MSVC\%MSVC_VER%\x64\Microsoft.VC143.CRT
set CODE_ROOT=%PROJECT_ROOT%\client_tools\lms\src\OPE_LMS
set RELEASE_BUILD_DIR=%CODE_ROOT%\build\Desktop_Qt_%QT_VER_FOLDER%_MSVC%MSVC_MAJOR_VER%_64bit-Release\release
set DEBUG_BUILD_DIR=%CODE_ROOT%\build\Desktop_Qt_%QT_VER_FOLDER%_MSVC%MSVC_MAJOR_VER%_64bit-Debug\debug

:: Setup Qt environment if not already done
if "%QT_ENV_SETUP%" NEQ "1" (
    call "%QT_PATH%/msvc%MSVC_MAJOR_VER%_64/bin/qtenv2.bat"
    call "C:\%PROGRAM_FILES%\Microsoft Visual Studio\%MSVC_MAJOR_VER%\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    set QT_ENV_SETUP=1
)

echo Building... [%BUILD_TYPE% mode]

:: Deploy for Release
if "%BUILD_TYPE%"=="release" goto :release
if "%BUILD_TYPE%"=="both" goto :release
goto :debug_check

:release
echo Deploying Release build...
%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin\windeployqt.exe %TRANSLATIONS% --force --compiler-runtime --qmldir "%CODE_ROOT%" --libdir "%RELEASE_BUILD_DIR%" --dir "%RELEASE_BUILD_DIR%" --plugindir "%RELEASE_BUILD_DIR%\plugins" "%RELEASE_BUILD_DIR%\OPE_LMS.exe"
echo "Copying MSVC Binaries to %RELEASE_BUILD_DIR%"
xcopy /Y "%MSVC_BINARIES%\*" "%RELEASE_BUILD_DIR%"

:debug_check
if "%BUILD_TYPE%"=="debug" goto :debug
if "%BUILD_TYPE%"=="both" goto :debug
goto :end

:debug
echo Deploying Debug build...
%QT_PATH%\msvc%MSVC_MAJOR_VER%_64\bin\windeployqt.exe %TRANSLATIONS% --force --compiler-runtime --qmldir "%CODE_ROOT%" --libdir "%DEBUG_BUILD_DIR%" --dir "%DEBUG_BUILD_DIR%" --plugindir "%DEBUG_BUILD_DIR%\plugins" "%DEBUG_BUILD_DIR%\OPE_LMS.exe"
echo "Copying MSVC Binaries to %DEBUG_BUILD_DIR%"
xcopy /Y "%MSVC_BINARIES%\*" "%DEBUG_BUILD_DIR%"

:end
echo Done Building!
endlocal
