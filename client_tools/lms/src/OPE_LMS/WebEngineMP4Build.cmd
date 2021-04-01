
rem
rem To allow MP4 videos in app, need to rebuild webengine
rem

rem Open QT command prompt for VS2019 x64

rem set VC_DIR=c:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC
set VC_DIR=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC

rem MSVC_VER=14.16.27023
set MSVC_VER=14.27.29110
rem set MSVC_VER=14.28.29333

rem Setup VCVars Build
"%VC_DIR%\Auxiliary\Build\vcvars64.bat" -vcvars_ver=%MSVC_VER%

rem Make sure python2 and build tools is in the path
rem Make sure python2.exe is visible in the path
rem path=c:\python27\;%path%
rem c:\qt\bin;
rem pull python3 from the path - needs python2
set path=c:\python27;%path%
rem set PATH=%PATH:C:\CSE_PORTABLE_CODE\VSCode\WPy32-3680\python-3.6.8;=%

rem Move to webengine folder
cd \Qt\5.15.2\Src\qtwebengine

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
qmake -- -webengine-proprietary-codecs

rem Tell nmake to use all cores
set CL=/MP

rem From webengine folder, start Build
"%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe"

echo Build done!!!!! - hit any key to install.
pause

rem Install - copy DLLs in place
"%VC_DIR%\Tools\MSVC\%MSVC_VER%\bin\Hostx64\x64\nmake.exe" install

rem change back to original directory
cd %~dp0
