QT += qml quick sql network quickcontrols2 webview networkauth webchannel webenginequick webenginecore webenginewidgets core5compat
#
#webengine webenginewidgets
# networkauth
# webengine webenginewidgets quick-private webview-private webview

CONFIG += c++11
# Hide -fms-compatibility-version warnings when using ms visual studio (D9002)
#QMAKE_LFLAGS += /ignore:D9002

# Enable console so we can print to stdout
CONFIG += console

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
    customlogger.cpp \
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
    openetworkaccessmanagerfactory.cpp \
    cm/cm_javascripthandler.cpp \
    cm/cm_websockettransport.cpp

RESOURCES += qml.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Additional import path used to resolve QML modules just for Qt Quick Designer
QML_DESIGNER_IMPORT_PATH =

# Hide duplicate include warnings - stupid ms c++...
QMAKE_LFLAGS += /ignore:4042

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x050F00
#QT_DEPRECATED_WARNINGS

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
    openetworkaccessmanagerfactory.h \
    cm/cm_javascripthandler.h \
    cm/cm_websockettransport.h \
    customlogger.h


RC_ICONS = logo_icon.ico

DISTFILES += \
    qt.conf \
    blue-folder.png \
    Scratch.txt \
    blue_sync.png \
    qtquickcontrols2.conf \
    upload_file.png \
    sync.png \
    logo_icon.png \
    logo_icon.ico \
    down_arrow.png \
    up_arrow.png \
    WebEngineMP4Build.cmd \
    websockettest.qml \
    qwebchannel.js \
    wc_index.html \
    opeWebViewClient.js \
    win_deploy.cmd \
    mail.png \
    mail_open.png \
    box.png \
    default_avatar.png \
    reply.png \
    new_message.png \
    StyledButton.qml \
    ReplyPopup.qml \
    NewMessagePopup.qml



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

#LIBS += -LC:/OpenSSL-Win64/lib # -lcrypto -lssl
#INCLUDEPATH += C:/OpenSSL-Win64/include
#OPEN_SSL_PATH = "C:/Program Files/OpenSSL-Win64"

#OPEN_SSL_PATH = "C:/OpenSSL-Win64"

#OPENSSL_PREFIX = "C:/"
OPEN_SSL_PATH = "C:/Qt/Tools/OpenSSL/Win_x64"
OPEN_SSL_DLL_PATH = $${OPEN_SSL_PATH}/bin
LIBS += -L"$${OPEN_SSL_PATH}/lib" #-llibcrypto -llibssl # -lcrypto -lssl
INCLUDEPATH += "$${OPEN_SSL_PATH}/include"


# Make sure we have files copied to the build folder
copy_files.commands = $(COPY_DIR) \"$$shell_path($$PWD\\www_content)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\web_content)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\logo_icon.ico)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\favicon.ico)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\web_content\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\qwebchannel.js)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\web_content\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\opeWebViewClient.js)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\web_content\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\mime_types.csv)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\qt.conf)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\" && \
    $(COPY_DIR) \"$$shell_path($$PWD\\qtquickcontrols2.conf)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\" && \
    $(COPY_DIR) \"$$shell_path($${OPEN_SSL_DLL_PATH}\\*.dll)\" \"$$shell_path($$OUT_PWD\\$$VARIANT\\)\"

first.depends = $(first) copy_files
export(first.depends)
export(copy_files.commands)
QMAKE_EXTRA_TARGETS += first copy_files
