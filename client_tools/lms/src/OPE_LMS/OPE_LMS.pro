QT += qml quick sql network quickcontrols2 webview networkauth
# networkauth
# webengine webenginewidgets quick-private webview-private webview

CONFIG += c++11

SOURCES += main.cpp \
    cm/file/cm_fileinfo.cpp \
    cm/file/cm_syncfile.cpp \
    cm/file/cm_syncfilechunk.cpp \
    cm/file/cm_syncfileversion.cpp \
    cm/school/sc_classes.cpp \
    cm/school/sc_classmodel.cpp \
    cm/school/sc_lessonitem.cpp \
    cm/school/sc_lessonitemmodel.cpp \
    cm/school/sc_modulemodel.cpp \
    cm/school/sc_modules.cpp \
    cm/school/sc_programmodel.cpp \
    cm/school/sc_programs.cpp \
    cm/cm_classroom.cpp \
    cm/cm_database.cpp \
    cm/cm_httpserver.cpp \
    cm/cm_machine.cpp \
    cm/cm_mimetypes.cpp \
    cm/cm_persistentobject.cpp \
    cm/cm_persistentobjectmodel.cpp \
    cm/cm_screengrab.cpp \
    cm/cm_sequentialguid.cpp \
    cm/cm_users.cpp \
    cm/cm_webrequest.cpp \
    external/ex_canvas.cpp \
    external/ex_ldap.cpp \
    appmodule.cpp \
    db.cpp \
    openetworkaccessmanagerfactory.cpp \
    cm/file/cm_fileinfo.cpp \
    cm/file/cm_syncfile.cpp \
    cm/file/cm_syncfilechunk.cpp \
    cm/file/cm_syncfileversion.cpp \
    cm/school/sc_classes.cpp \
    cm/school/sc_classmodel.cpp \
    cm/school/sc_lessonitem.cpp \
    cm/school/sc_lessonitemmodel.cpp \
    cm/school/sc_modulemodel.cpp \
    cm/school/sc_modules.cpp \
    cm/school/sc_programmodel.cpp \
    cm/school/sc_programs.cpp \
    cm/cm_classroom.cpp \
    cm/cm_database.cpp \
    cm/cm_httpserver.cpp \
    cm/cm_machine.cpp \
    cm/cm_mimetypes.cpp \
    cm/cm_persistentobject.cpp \
    cm/cm_persistentobjectmodel.cpp \
    cm/cm_screengrab.cpp \
    cm/cm_sequentialguid.cpp \
    cm/cm_users.cpp \
    cm/cm_webrequest.cpp \
    external/ex_canvas.cpp \
    external/ex_ldap.cpp \
    appmodule.cpp \
    db.cpp \
    main.cpp \
    openetworkaccessmanagerfactory.cpp

RESOURCES += qml.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Additional import path used to resolve QML modules just for Qt Quick Designer
QML_DESIGNER_IMPORT_PATH =

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

HEADERS += \
    cm/file/cm_fileinfo.h \
    cm/file/cm_syncfile.h \
    cm/file/cm_syncfilechunk.h \
    cm/file/cm_syncfileversion.h \
    cm/school/sc_classes.h \
    cm/school/sc_classmodel.h \
    cm/school/sc_lessonitem.h \
    cm/school/sc_lessonitemmodel.h \
    cm/school/sc_modulemodel.h \
    cm/school/sc_modules.h \
    cm/school/sc_programmodel.h \
    cm/school/sc_programs.h \
    cm/cm_classroom.h \
    cm/cm_database.h \
    cm/cm_httpserver.h \
    cm/cm_machine.h \
    cm/cm_mimetypes.h \
    cm/cm_persistentobject.h \
    cm/cm_persistentobjectmodel.h \
    cm/cm_screengrab.h \
    cm/cm_sequentialguid.h \
    cm/cm_users.h \
    cm/cm_webrequest.h \
    external/ex_canvas.h \
    external/ex_ldap.h \
    appmodule.h \
    db.h \
    openetworkaccessmanagerfactory.h \
    cm/file/cm_fileinfo.h \
    cm/file/cm_syncfile.h \
    cm/file/cm_syncfilechunk.h \
    cm/file/cm_syncfileversion.h \
    cm/school/sc_classes.h \
    cm/school/sc_classmodel.h \
    cm/school/sc_lessonitem.h \
    cm/school/sc_lessonitemmodel.h \
    cm/school/sc_modulemodel.h \
    cm/school/sc_modules.h \
    cm/school/sc_programmodel.h \
    cm/school/sc_programs.h \
    cm/cm_classroom.h \
    cm/cm_database.h \
    cm/cm_httpserver.h \
    cm/cm_machine.h \
    cm/cm_mimetypes.h \
    cm/cm_persistentobject.h \
    cm/cm_persistentobjectmodel.h \
    cm/cm_screengrab.h \
    cm/cm_sequentialguid.h \
    cm/cm_users.h \
    cm/cm_webrequest.h \
    external/ex_canvas.h \
    external/ex_ldap.h \
    appmodule.h \
    db.h \
    openetworkaccessmanagerfactory.h

LIBS += -LC:/OpenSSL-Win64/lib # -lcrypto -lssl
INCLUDEPATH += C:/OpenSSL-Win64/include

RC_ICONS = logo_icon.ico

DISTFILES += \
    qt.conf \
    blue-folder.png \
    Scratch.txt \
    blue_sync.png \
    upload_file.png \
    sync.png \
    logo_icon.png \
    logo_icon.ico \
    down_arrow.png \
    up_arrow.png \
    www_content/projekktor-1.3.09/._jquery-1.9.1.min.js \
    www_content/projekktor-1.3.09/._projekktor-1.3.09.js \
    www_content/projekktor-1.3.09/._projekktor-1.3.09.min.js \
    www_content/projekktor-1.3.09/._projekktor-1.3.09.pre-min.js \
    www_content/projekktor-1.3.09/jquery-1.9.1.min.js \
    www_content/projekktor-1.3.09/projekktor-1.3.09.js \
    www_content/projekktor-1.3.09/projekktor-1.3.09.min.js \
    www_content/projekktor-1.3.09/projekktor-1.3.09.pre-min.js \
    www_content/ViewerJS/compatibility.js \
    www_content/ViewerJS/pdf.js \
    www_content/ViewerJS/pdf.worker.js \
    www_content/ViewerJS/pdfjsversion.js \
    www_content/ViewerJS/text_layer_builder.js \
    www_content/ViewerJS/ui_utils.js \
    www_content/ViewerJS/webodf.js \
    www_content/projekktor-1.3.09/swf/._Jarisplayer \
    www_content/projekktor-1.3.09/swf/._StrobeMediaPlayback \
    www_content/projekktor-1.3.09/themes/._maccaco \
    www_content/projekktor-1.3.09/._media \
    www_content/projekktor-1.3.09/._projekktor-1.3.09.min.map \
    www_content/projekktor-1.3.09/._swf \
    www_content/projekktor-1.3.09/._themes \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/._SmoothStreamingPlugin_EULA.rtf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/SmoothStreamingPlugin_EULA.rtf \
    www_content/projekktor-1.3.09/swf/Jarisplayer/._jarisplayer.swf \
    www_content/projekktor-1.3.09/swf/Jarisplayer/jarisplayer.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/._StrobeMediaPlayback.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/._StrobeMediaPlayback_hls.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/._StrobeMediaPlayback_hls_mss.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/._StrobeMediaPlayback_mss.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/StrobeMediaPlayback.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/StrobeMediaPlayback_hls.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/StrobeMediaPlayback_hls_mss.swf \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/StrobeMediaPlayback_mss.swf \
    www_content/projekktor-1.3.09/themes/maccaco/._buffering.gif \
    www_content/projekktor-1.3.09/themes/maccaco/._maccaco-load.gif \
    www_content/projekktor-1.3.09/themes/maccaco/._noise.gif \
    www_content/projekktor-1.3.09/themes/maccaco/buffering.gif \
    www_content/projekktor-1.3.09/themes/maccaco/maccaco-load.gif \
    www_content/projekktor-1.3.09/themes/maccaco/noise.gif \
    www_content/projekktor-1.3.09/themes/._layout-grid.gif \
    www_content/projekktor-1.3.09/themes/layout-grid.gif \
    www_content/projekktor-1.3.09/media/._intro.png \
    www_content/projekktor-1.3.09/media/intro.png \
    www_content/projekktor-1.3.09/themes/maccaco/._maccaco-load-static.png \
    www_content/projekktor-1.3.09/themes/maccaco/._maccaco.png \
    www_content/projekktor-1.3.09/themes/maccaco/._start.png \
    www_content/projekktor-1.3.09/themes/maccaco/maccaco-load-static.png \
    www_content/projekktor-1.3.09/themes/maccaco/maccaco.png \
    www_content/projekktor-1.3.09/themes/maccaco/start.png \
    www_content/ViewerJS/images/kogmbh.png \
    www_content/ViewerJS/images/nlnet.png \
    www_content/ViewerJS/images/texture.png \
    www_content/ViewerJS/images/toolbarButton-download.png \
    www_content/ViewerJS/images/toolbarButton-fullscreen.png \
    www_content/ViewerJS/images/toolbarButton-menuArrows.png \
    www_content/ViewerJS/images/toolbarButton-pageDown.png \
    www_content/ViewerJS/images/toolbarButton-pageUp.png \
    www_content/ViewerJS/images/toolbarButton-presentation.png \
    www_content/ViewerJS/images/toolbarButton-zoomIn.png \
    www_content/ViewerJS/images/toolbarButton-zoomOut.png \
    www_content/projekktor-1.3.09/themes/maccaco/._maccaco.psd \
    www_content/projekktor-1.3.09/themes/maccaco/maccaco.psd \
    www_content/projekktor-1.3.09/themes/maccaco/._projekktor.style.css \
    www_content/projekktor-1.3.09/themes/maccaco/projekktor.style.css \
    www_content/ViewerJS/example.local.css \
    www_content/projekktor-1.3.09/themes/._design.html \
    www_content/projekktor-1.3.09/themes/design.html \
    www_content/projekktor-1.3.09/._readme.html \
    www_content/projekktor-1.3.09/readme.html \
    www_content/ViewerJS/index.html \
    www_content/player.html \
    www_content/projekktor-1.3.09/swf/Jarisplayer/._license.txt \
    www_content/projekktor-1.3.09/swf/Jarisplayer/license.txt \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/._license.txt \
    www_content/projekktor-1.3.09/swf/StrobeMediaPlayback/license.txt \
    www_content/projekktor-1.3.09/projekktor-1.3.09.min.map \
    www_content/projekktor-1.3.09/media/._intro.mp4 \
    www_content/projekktor-1.3.09/media/intro.mp4 \
    www_content/projekktor-1.3.09/media/._intro.ogv \
    www_content/projekktor-1.3.09/media/intro.ogv \
    www_content/projekktor-1.3.09/media/._intro.webm \
    www_content/projekktor-1.3.09/media/intro.webm \
    WebEngineMP4Build.txt

# Rules to force qrc rebuild each time - deal with bug where qml files aren't updated on next run
update_qml.target = qml.qrc
update_qml.commands = echo>>$${update_qml.target} # same as touch
update_qml.depends = $$files($${PWD}/*.qml, true) # recurse into subdirs
QMAKE_EXTRA_TARGETS += update_qml
PRE_TARGETDEPS += $${update_qml.target}

# DEPLOYMENT STUFF - Copy Binary files to build folder
CONFIG (debug, debug|release) {
    VARIANT = debug
} else {
    VARIANT = release
}

copy_files.commands = $(COPY_DIR) \"$$shell_path($$PWD\\www_content)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\web_content)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\logo_icon.ico)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\logo_icon.ico)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\favicon.ico)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\qt.conf)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\"
first.depends = $(first) copy_files
export(first.depends)
export(copy_files.commands)
QMAKE_EXTRA_TARGETS += first copy_files
