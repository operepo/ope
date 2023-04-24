@echo off
rem
rem To allow MP4 videos in app, need to rebuild webengine
rem

echo NOTE - This needs to run from a clean command prompt - NOT the QT command prompt
echo Also this needs to run with an unconfigured source tree - it will configure the qtwebengine module only
pause

REM Updated for QT 6.5

rem NOTE - Set appropriate paths here
set QT_PATH=C:\Qt\6.5.0
set PYTHONPATH=C:\Program Files\Python39
set VC_EDITION=Community
set MSVC_VER=14.29.30133
set MSVC_MAJOR_VER=2019

set VC_DIR=C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC

REM Set up Microsoft Visual Studio 2019, where <arch> is amd64, x86, etc.
rem Setup VCVars Build
SET PATH=%PYTHONPATH%;%QT_PATH%\Src\qtbase\bin;C:\Qt\Tools\Ninja;%PATH%;

call "%QT_PATH%/msvc%MSVC_MAJOR_VER%_64/bin/qtenv2.bat"

CALL "%VC_DIR%\Auxiliary\Build\vcvarsall.bat" amd64




echo Ready to build, press any key when ready...
rem change back to original directory
cd %~dp0
pause


rem Configure options
rem NOTE - need to remove OLD cache or it won't rescan stuff
rem "%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" clean
rem "%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" distclean
rem WHAT FILES TO PROPERLY CLEAN?
rem del config.cache /a /s
rem del .qmake.cache /a /s
rem del .qmake.stash /a /s
rem del .qmake.conf  /a /s
rem   .super, .summary?
rem - too much? del Makefile /a /s
rem qmake -- -webengine-proprietary-codecs

rem Tell nmake to use all cores
set CL=/MP

rem Start with a fresh copy of source - don't run configure.bat in root folder
rem echo Configuring QT Src folder...
rem cd %QT_PATH%\Src
rem -no-feature-vulkan ??
rem call configure.bat -no-feature-vulkan

echo Configuring qtwebengine with proprietary codecs
rem Move to webengine folder
cd %QT_PATH%\Src\qtwebengine
CALL qt-configure-module . -webengine-proprietary-codecs -webengine-pepper-plugins -webengine-printing-and-pdf -webengine-spellchecker
rem doesn't work to disable vulkan? -no-feature-vulkan
rem change back to original directory
cd %~dp0

echo Building qtwebengine...
pause
rem Move to webengine folder
cd %QT_PATH%\Src\qtwebengine
cmake --build . --parallel --fresh
rem change back to original directory
cd %~dp0

echo If no errors above, ready to install...
pause
rem Move to webengine folder
cd %QT_PATH%\Src\qtwebengine
cmake --install .
rem install the debug versions of the files too
cmake --install . --config Debug
rem change back to original directory
cd %~dp0

rem From webengine folder, start Build
rem "%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe"

echo Build done!!!!! - hit any key to install.
pause

rem Install - copy DLLs in place
rem "%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" install

rem change back to original directory
cd %~dp0
