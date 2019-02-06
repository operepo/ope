
rem
rem To allow MP4 videos in app, need to rebuild webengine
rem

rem Open QT command prompt for VS2017 x64

rem Setup VCVars Build
"c:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build\vcvars64.bat"

rem Make sure python2 and build tools is in the path
path=c:\qt\bin;c:\python27\;%path%

rem Move to webengine folder
cd \Qt\5.12.0\Src\qtwebengine

rem Configure options
qmake -- -webengine-proprietary-codecs

rem Tell nmake to use all cores
set CL=/MP

rem From webengine folder, start Build
"C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Tools\MSVC\14.16.27023\bin\Hostx64\x64\nmake.exe"

echo Build done!!!!! - hit any key to install.
pause

rem Install - copy DLLs in place
"C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Tools\MSVC\14.16.27023\bin\Hostx64\x64\nmake.exe" install
