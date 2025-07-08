
@echo off
set VERSION=24.9.5.0


for /f "delims=" %%i in ('python -c "import sys; print(sys.prefix)"') do set py_root_path=%%i
echo Python root path: %py_root_path%

echo Pre-importing kivy modules to ensure they are included
python -c "import kivy.uix.recycleview; import kivy.uix.recycleview.datamodel; import kivy.uix.recycleview.layout; import kivy.uix.recycleview.views; print('Kivy RecycleView modules imported successfully')"

python -m nuitka ^
    --standalone ^
    --file-reference-choice=runtime ^
    --mingw64 ^
    --windows-icon-from-ico=logo_icon.ico ^
    --windows-company-name=OPE_PROJECT ^
    --windows-product-name=SyncAPp ^
    --windows-file-version=%VERSION% ^
    --windows-product-version=%VERSION% ^
    --windows-file-description="Admin SyncApp - deploy or update OPE servers." ^
    --disable-plugin=numpy --disable-plugin=tk-inter --disable-plugin=pyqt5 --disable-plugin=pyside2 ^
    --include-package=kivy --include-package=requests --enable-plugin=kivy --include-package=kivy.uix --include-package=kivy.uix.recycleview --include-package=kivy.uix.recycleview.datamodel --include-package=kivy.uix.recycleview.layout --include-package=kivy.uix.recycleview.views --include-package=kivy.uix.recycleboxlayout --include-package=kivy.uix.recyclegridlayout --include-package=kivy.factory_registers --include-module=kivy.uix.recycleview.__init__ --include-module=kivy.uix.recycleview.datamodel --include-module=kivy.uix.recycleview.layout --include-module=kivy.uix.recycleview.views ^
    --include-data-file="%py_root_path%\share\angle\bin\*.dll=./" ^
    --include-data-dir="%py_root_path%\Lib\site-packages\kivy\uix\recycleview=./kivy/uix/recycleview" ^
    --include-data-file="*.kv=./" ^
    --include-data-file="*.json=./" ^
    --include-data-file="*.ico=./" ^
    --include-data-file="*.png=./" ^
    --include-data-file="*.md=./" ^
    --follow-imports ^
    --follow-import-to=kivy.uix.recycleview,kivy.uix.recycleview.datamodel,kivy.uix.recycleview.layout,kivy.uix.recycleview.views ^
    --output-filename=SyncApp.exe ^
    sync_gui.py


echo Copying kivy uix files to dist folder
xcopy /yS %py_root_path%\Lib\site-packages\kivy\uix\* .\sync_gui.dist\kivy\uix\

echo Copying kivy factory files to dist folder
xcopy /yS %py_root_path%\Lib\site-packages\kivy\factory* .\sync_gui.dist\kivy\

echo Copying kivy core files to dist folder
xcopy /yS %py_root_path%\Lib\site-packages\kivy\core\* .\sync_gui.dist\kivy\core\
