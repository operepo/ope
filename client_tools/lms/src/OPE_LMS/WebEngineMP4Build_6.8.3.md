# QtWebEngine Build Guide for Windows

This guide provides step-by-step instructions for building QtWebEngine on Windows, following the [official Qt documentation](https://wiki.qt.io/QtWebEngine/Qt6Build).

## Prerequisites

### Required Software
1. **Qt 6.8.3**
2. **Visual Studio Community 2022**
3. **Node.js**
4. **Python 3** with html5lib
5. **Gperf** (install via Chocolatey)
   ```powershell
   choco install gperf
   ```
6. **Win Flex-Bison**
   - Download from [SourceForge](https://sourceforge.net/projects/winflexbison/)
   - Copy to Program Files
   - Add to system PATH
7. **Bison** 
   - Download from [SourceForge](https://sourceforge.net/projects/gnuwin32/)
   - Add to system PATH
8. **Perl** [Strawberry](https://strawberryperl.com/) (required for compiling opus without optimizations)

## Build Instructions

### 1. Clone Repository
```powershell
mkdir qt6
cd qt6
git clone git://code.qt.io/qt/qtwebengine.git
cd qtwebengine
```

### 2. Initialize Submodules
```powershell
git submodule init
git submodule update
git checkout origin/6.8.3
git submodule update
```

### 3. Create Build Directory
```powershell
mkdir build
cd build
```

### 4. Configure Environment
Open a new Command Prompt (cmd) and set the following environment variables. Adjust paths and versions according to your system:

```batch
set QT_PATH=C:\Qt\6.8.3
set PYTHONPATH=C:\Users\Administrator\AppData\Local\Programs\Python\Python313\
set VC_EDITION=Community
set MSVC_VER=14.44.35207
set MSVC_MAJOR_VER=2022
set PROGRAM_FILES=Program Files

set VC_DIR=C:\%PROGRAM_FILES%\Microsoft Visual Studio\%MSVC_MAJOR_VER%\%VC_EDITION%\VC

rem Setup VCVars Build
SET PATH=%PYTHONPATH%;%QT_PATH%\Src\qtbase\bin;C:\Qt\Tools\Ninja;%PATH%;

rem Initialize Qt Environment
"%QT_PATH%/msvc%MSVC_MAJOR_VER%_64/bin/qtenv2.bat"

rem Initialize Visual Studio Environment
"%VC_DIR%\Auxiliary\Build\vcvarsall.bat" x64
```

### 5. Build QtWebEngine
```batch
cd build
qt-configure-module . -webengine-proprietary-codecs -webengine-pepper-plugins -webengine-printing-and-pdf -webengine-spellchecker
cmake --build . --parallel --clean-first
cmake --install .
cmake --install . --config debug
```

## Troubleshooting

### Common Error: Non-static Member Function Call
If you encounter the error:
```
error C2352: 'cppgc::internal::MarkingStateBase::MarkNoPush': a call of a non-static member function requires an object
```

#### Solution 1: Using Compiler Flag
```batch
qt-configure-module . -webengine-proprietary-codecs -webengine-pepper-plugins -webengine-printing-and-pdf -webengine-spellchecker -- -DCMAKE_CXX_FLAGS="/D_ALLOW_QUALIFIED_MEMBER_ACCESS=1"
```

#### Solution 2: Using Patch
1. Create patches directory:
   ```batch
   mkdir patches
   ```

2. Create patch file `marking-state.patch`:
   ```diff
   diff --git a/src/3rdparty/chromium/v8/src/heap/cppgc/marking-state.h b/src/3rdparty/chromium/v8/src/heap/cppgc/marking-state.h
   --- a/src/3rdparty/chromium/v8/src/heap/cppgc/marking-state.h
   +++ b/src/3rdparty/chromium/v8/src/heap/cppgc/marking-state.h
   @@ -361,1 +361,1 @@
   -    return MutatorMarkingState::BasicMarkingState::MarkNoPush(header);
   +    return this->BasicMarkingState::MarkNoPush(header);
   ```

3. Apply the patch:
   ```batch
   git apply patches/marking-state.patch
   ```
