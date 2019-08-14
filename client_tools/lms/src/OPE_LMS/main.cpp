#include <QGuiApplication>
#include <QQmlApplicationEngine>
// #include <QMessageBox>
#include <QTextCodec>
#include <QtWebView/QtWebView>
#include <QtWebEngine/qtwebengineglobal.h>
#include <QIcon>

#include <QtGlobal>
#include <QtDebug>
#include <QTextStream>
#include <QTextCodec>
#include <QLocale>
#include <QTime>
#include <QFile>
#include <QLockFile>

#include "openetworkaccessmanagerfactory.h"
#include "appmodule.h"
#include "customlogger.h"



int main(int argc, char *argv[])
{

    //QRegularExpression regex("(\\\"\\s*:\\s*)([0-9.]+)(\\s*[,])");
    //QString json = "{\"id\": 230842309483209, \"test\": \"test2\"}";
    //json = json.replace(regex, "\\1\"\\2\"\\3");  //  :\"\\1\",");
    //qDebug() << json;
    //return 0;

    // Set global app parameters - used by settings later
    QCoreApplication::setOrganizationName("OPE");
    QCoreApplication::setOrganizationDomain("openprisoneducation.com");
    QCoreApplication::setApplicationName("OPELMS");

    log_file_path = QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/debug.log";

    qDebug() << log_file_path;
    // Are we running in the Qt Creator IDE?
    QByteArray envVar = qgetenv("QTDIR");
    if (envVar.isEmpty()) {
        qDebug() << "Running outside IDE";
        is_in_IDE = false;
        log_to_file = true;

        // Install custom log handler
        qInstallMessageHandler(customLogOutput);
    } else {
        qDebug() << "Running within IDE";
        is_in_IDE = true;
        log_to_file = false;
    }

    // Prevent app from running twice
    QString tmp_dir = QDir::tempPath();
    QLockFile lf(tmp_dir + "/ope_lms.lock");

    if (!lf.tryLock(100))
    {
        qDebug() << "=====================================================\n" <<
                    "WARNING - App already running, exiting...\n" <<
                    "only one instance allowed to run. If this is an " <<
                    " error, remove the temp/ope_lms.lock file and try again" <<
                    "=====================================================\n";
        return 1;
    }


    // Show SSL info
    qDebug() << "SSL Library Info: " << QSslSocket::supportsSsl() << QSslSocket::sslLibraryBuildVersionString() << QSslSocket::sslLibraryVersionString();

    // Relax ssl config as we will be running through test certs
    QSslConfiguration sslconf = QSslConfiguration::defaultConfiguration();
    QList<QSslCertificate> cert_list = sslconf.caCertificates();
    QList<QSslCertificate> cert_new = QSslCertificate::fromData("CaCertificates");
    cert_list += cert_new;
    sslconf.setCaCertificates(cert_list);
    sslconf.setProtocol(QSsl::AnyProtocol);
    sslconf.setPeerVerifyMode(QSslSocket::VerifyNone);
    sslconf.setSslOption(QSsl::SslOptionDisableServerNameIndication,true);
    QSslConfiguration::setDefaultConfiguration(sslconf);


    //QTextCodec::setCodecForLocale(QTextCodec::codecForName("UTF-8"));
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    // Possible help for high contrast refresh?
    QGuiApplication::setAttribute(Qt::AA_UseOpenGLES);

    QGuiApplication app(argc, argv);
    // Put our local folder as first path to look at for dlls
    QCoreApplication::addLibraryPath(QCoreApplication::applicationDirPath());
    qDebug() << "Library Paths: " << QCoreApplication::libraryPaths();

    // NOTE: Need this right after GUI App creation
    QtWebView::initialize();
    //QtWebEngine::initialize();

    app.setWindowIcon(QIcon(":/images/logo_icon.ico"));

    QLoggingCategory::setFilterRules(QStringLiteral("qt.qml.binding.removal.info=true"));

    QQmlApplicationEngine engine;

    // -- Setup our app module which deals with QML/C++ integration
    AppModule *appModule = new AppModule(&engine);

    QString loadPage = "qrc:/lms.qml";
    //loadPage = "qrc:/websockettest.qml";


    QString last_arg = QCoreApplication::arguments().last();

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

    return app.exec();
}
