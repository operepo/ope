#include <QGuiApplication>
#include <QApplication>
#include <QCoreApplication>
#include <QQmlApplicationEngine>
// #include <QMessageBox>
#include <QTextCodec>
#include <QtWebView/QtWebView>
//#include <QtWebEngine/qtwebengineglobal.h>
#include <QtWebEngineCore>
#include <QWebEngineProfile>
#include <QWebEngineSettings>

#include <QIcon>

#include <QtGlobal>
#include <QtDebug>
#include <QTextStream>
#include <QLocale>
#include <QTime>
#include <QFile>
#include <QOperatingSystemVersion>

//#include <QTranslator>

#include <windows.h>

//#include "openetworkaccessmanagerfactory.h"
#include "appmodule.h"
#include "customlogger.h"

// Needed to pull in windows functions
#pragma comment(lib,"user32.lib")

QT_REQUIRE_CONFIG(ssl);

QString pgdata_path = "";

int main(int argc, char *argv[])
{
    // Dummy variable to force rebuild
#define rebuilding 19;

    // Hide the console window
#if defined( Q_OS_WIN )
        ShowWindow( GetConsoleWindow(), SW_HIDE ); //hide console window
        // SW_NORMAL - to show console
#endif

    //QRegularExpression regex("(\\\"\\s*:\\s*)([0-9.]+)(\\s*[,])");
    //QString json = "{\"id\": 230842309483209, \"test\": \"test2\"}";
    //json = json.replace(regex, "\\1\"\\2\"\\3");  //  :\"\\1\",");
    //qDebug() << json;
    //return 0;

    // Set global app parameters - used by settings later
    QCoreApplication::setOrganizationName("OPE");
    QCoreApplication::setOrganizationDomain("openprisoneducation.com");
    QCoreApplication::setApplicationName("OPELMS");

    // Change cache/local data paths to point to programdata folder instead of user account - allows syncing/usage before user has logged in
#if defined( Q_OS_WIN )
    // Set environment so that it uses the new path
    pgdata_path = QStandardPaths::standardLocations(QStandardPaths::AppConfigLocation).at(1); // grab 2nd item
    // Remove app name (c:/programdata/ope/opelms -> c:/programdata/ope)
    pgdata_path = pgdata_path.replace("/OPELMS", "");
    //qDebug() << "PG Data Path: " << pgdata_path;
    QString cache_path = qEnvironmentVariable("QML_DISK_CACHE_PATH", pgdata_path + "/tmp/qmlcache/");
    //qDebug() << "Cache Path: " << cache_path;
    qputenv("QML_DISK_CACHE_PATH", cache_path.toStdString());

#endif

    //QTextCodec::setCodecForLocale(QTextCodec::codecForName("UTF-8"));
    // Not needed in qt6
    //QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    // Possible help for high contrast refresh?
    // Not available in qt6
    //QGuiApplication::setAttribute(Qt::AA_UseOpenGLES);
    QCoreApplication::setAttribute(Qt::AA_ShareOpenGLContexts);
    //QApplication::setAttribute(Qt::AA_DisableWindowContextHelpButton);

    // NOTE: Need before now?  - - Need this right after GUI App creation
    //QtWebEngine::initialize();
    //QtWebView::initialize();

    log_file_path = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation) + "/lms_app_debug.log";
    // In windows - put it in programdata/ope/tmp/logs/debug.log
    if (QOperatingSystemVersion::currentType() == QOperatingSystemVersion::Windows) {
        // returns ("c:/users/<USER>/AppData/Local/<APPNAME>", "c:/programdata/<APPNAME>")
        // NOTE - Will need to adjust this if
        //QDir d = QDir(QStandardPaths::standardLocations(QStandardPaths::AppConfigLocation).at(1));
        //qDebug() << "AppConfigLocation: " << d.path();
        //d.cdUp(); // Move back to c:/programdata
        //log_file_path = d.path() + "/tmp/log/lms_app_debug.log";
        log_file_path = pgdata_path + "/tmp/log/lms_app_debug.log";
    }
    qDebug() << "Logging to: " << log_file_path;

    // Are we running in the Qt Creator IDE?
    QByteArray envVar = qgetenv("QTDIR");
    if (envVar.isEmpty()) {
        //qDebug() << "Running outside IDE";
        is_in_IDE = false;
        log_to_file = true;

        // Install custom log handler
        qInstallMessageHandler(customLogOutput);
    } else {
        qDebug() << "Running within IDE";
        is_in_IDE = true;
        log_to_file = false;
    }


    QString last_arg = ""; //QCoreApplication::arguments().last();
    last_arg = argv[argc-1];

    //qDebug() << "Last arg: " << last_arg;
    //out << "Testing stdout..." << Qt::endl;

    // Do we need to run headless (quiet_sync?)
    if (last_arg == "quiet_sync") {
        quiet_mode = true;
        // Show the console window
#if defined( Q_OS_WIN )
        ShowWindow( GetConsoleWindow(), SW_NORMAL ); //hide console window
        // SW_NORMAL - to show console
#endif
        qDebug() << "Running quiet_sync - headless mode...";
        QCoreApplication cmd_app(argc, argv);

        QQmlApplicationEngine cmd_engine;

        // -- Setup our app module which deals with QML/C++ integration
        AppModule *cmd_appModule = new AppModule(&cmd_engine, pgdata_path);

        // Sync from command line, then exit.
        if (cmd_appModule->isAppCredentialed() != true) {
            // Can't sync if app not credentialed.
            qDebug() << "ERROR - Can't sync app when not credentialed!";
            return -1;
        }

        qDebug() << "Launching syncLMSQuiet...";
        // Run sync in quiet mode then exit.
        QTimer::singleShot(1, cmd_appModule,  SLOT(syncLMSQuiet()));
        return cmd_app.exec();
    }

    //QGuiApplication app(argc, argv);
    QApplication app(argc, argv);
//    QTranslator translator;
//    bool translator_ret = translator.load(":/translations_en.qm");
//    app.installTranslator(&translator);

    // Put our local folders as first path to look at for dlls
    QCoreApplication::addLibraryPath(QCoreApplication::applicationDirPath() + "/lib");
    QCoreApplication::addLibraryPath(QCoreApplication::applicationDirPath());
    qDebug() << "Library Paths: " << QCoreApplication::libraryPaths();

    // NOTE: Need this right after GUI App creation? QtWebengine init earlier?
    QtWebView::initialize();

    app.setWindowIcon(QIcon(":/images/logo_icon.ico"));

    QLoggingCategory::setFilterRules(QStringLiteral("qt.qml.binding.removal.info=true"));

    // Init webview settings
    // Changed in qt6
//    QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::PluginsEnabled, true);
//    QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::FullScreenSupportEnabled, true);
//    QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::AllowWindowActivationFromJavaScript, true);
//    QWebEngineSettings::defaultSettings()->setAttribute(QWebEngineSettings::PdfViewerEnabled, true);

    QWebEngineProfile::defaultProfile()->settings()->setAttribute(QWebEngineSettings::PluginsEnabled, true);
    QWebEngineProfile::defaultProfile()->settings()->setAttribute(QWebEngineSettings::FullScreenSupportEnabled, true);
    QWebEngineProfile::defaultProfile()->settings()->setAttribute(QWebEngineSettings::AllowWindowActivationFromJavaScript, true);
    QWebEngineProfile::defaultProfile()->settings()->setAttribute(QWebEngineSettings::PdfViewerEnabled, true);
    QWebEngineProfile::defaultProfile()->settings()->setAttribute(QWebEngineSettings::DnsPrefetchEnabled, true);
    // Disable accessibility in debug mode to prevent crash
/*#if defined( QT_DEBUG )
    qDebug() << "Disabling accessibility in debug mode...";
    QWebEngineProfile::defaultProfile()->setHttpUserAgent(
        QWebEngineProfile::defaultProfile()->httpUserAgent() + " QTWEBENGINE_DISABLE_ACCESSIBILITY/1.0"
    );
    QWebEngineProfile::defaultProfile()->setSpellCheckEnabled(false);
#endif*/


    QQmlApplicationEngine engine;

    // -- Setup our app module which deals with QML/C++ integration
    AppModule *appModule = new AppModule(&engine, pgdata_path);

    QString loadPage = "qrc:/lms.qml";
    //loadPage = "qrc:/websockettest.qml";
    //

    bool is_app_credentialed = appModule->isAppCredentialed();
    if (is_app_credentialed != true) {
        // Load the error page for non credentialed apps
        loadPage = "qrc:/not_credentialed.qml";
    }

    bool need_sync = false;
    if (last_arg == "sync" || appModule->hasAppSycnedWithCanvas() != true)
    {
        need_sync = true;
    }

    // Set the need_sync attribute
    QQmlContext *context = engine.rootContext();
    context->setContextProperty(QStringLiteral("need_sync"), need_sync);

    //engine.load(QUrl(QLatin1String("qrc:/dropTest.qml")));
    engine.load(QUrl(loadPage));

    int e = app.exec();
    // Needed to exit when a console window exists but is hidden
    // Don't kill parent console - it kills process too?
    // exit(e);
    return e;
}
//////////////////
