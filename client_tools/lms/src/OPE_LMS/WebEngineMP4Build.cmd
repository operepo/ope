
rem
rem To allow MP4 videos in app, need to rebuild webengine
rem

set QT_VERSION=6.3.0

set QT_PATH=C:\Qt\%QT_VERSION%

set VC_EDITION=Community
set MSVC_VER=14.29.30133
set MSVC_MAJOR_VER=2019

rem set VC_DIR=c:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC
set VC_DIR=C:\Program Files (x86)\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC

rem MSVC_VER=14.16.27023
rem ** set MSVC_VER=14.27.29110
set MSVC_VER=14.29.30133
rem set MSVC_VER=14.28.29333

rem Setup VCVars Build
call "%QT_PATH%/msvc%MSVC_MAJOR_VER%_64/bin/qtenv2.bat"
rem call "%VC_DIR%\Auxiliary\Build\vcvars64.bat" -vcvars_ver=%MSVC_VER%
call "%VC_DIR%\Auxiliary\Build\vcvarsall.bat" amd64


rem Make sure python2 and build tools is in the path
rem Make sure python2.exe is visible in the path
rem path=c:\python27\;C:\win_flex_bison-2.5.25;%path%
rem c:\qt\bin;
rem pull python3 from the path - needs python2
set path=c:\python27;%path%
set path=C:\win_flex_bison-2.5.25;%path%
rem set PATH=%PATH:C:\CSE_PORTABLE_CODE\VSCode\WPy32-3680\python-3.6.8;=%

rem Move to webengine folder
cd \Qt\%QT_VERSION%\Src\qtwebengine

rem Configure options
rem NOTE - need to remove OLD cache or it won't rescan stuff
"%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" clean
"%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" distclean
rem WHAT FILES TO PROPERLY CLEAN?
del config.cache /a /s
del .qmake.cache /a /s
del .qmake.stash /a /s
del .qmake.conf  /a /s
rem   .super, .summary?
rem - too much? del Makefile /a /s
rem qmake -- -webengine-proprietary-codecs

rem Tell nmake to use all cores
set CL=/MP

qt-configure-module . -webengine-proprietary-codecs -webengine-pepper-plugins -webengine-printing-and-pdf
cmake --build . --parallel
cmake --install .

rem From webengine folder, start Build
rem "%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe"

echo Build done!!!!! - hit any key to install.
pause

rem Install - copy DLLs in place
rem "%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" install

rem change back to original directory
cd %~dp0
