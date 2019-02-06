#include <QGuiApplication>
#include <QQmlApplicationEngine>
//#include <QMessageBox>
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

#include "openetworkaccessmanagerfactory.h"
#include "appmodule.h"

// Values for custom log handler
QString log_file_path = "/debug.log";
bool log_to_file = true;
bool is_in_IDE = false;
QFile log_file;

void customLogOutput(QtMsgType type, const QMessageLogContext &context,
                     const QString &msg) {
    QHash<QtMsgType, QString> msgLevelHash({{QtDebugMsg, "Debug"},
                                            {QtInfoMsg, "Info"},
                                            {QtWarningMsg, "Warning"},
                                            {QtCriticalMsg, "Critical"},
                                            {QtFatalMsg, "Fatal"}});
    QByteArray localMsg = msg.toLocal8Bit();
    QTime time = QTime::currentTime();
    QString formattedTime = time.toString("hh:mm:ss.zzz");
    QByteArray formattedTimeMsg = formattedTime.toLocal8Bit();
    QString logLevelName = msgLevelHash[type];
    QByteArray logLevelMsg = logLevelName.toLocal8Bit();

    if (log_to_file) {
        QString txt = QString("%1 %2: %3 (%4)").arg(formattedTime, logLevelName,
                                                    msg, context.file);
        if (!log_file.isOpen()) {
            log_file.setFileName(log_file_path);
            log_file.open(QIODevice::WriteOnly | QIODevice::Append);
        }

        QTextStream ts(&log_file);
        ts << txt << endl;

    } else {
        fprintf(stderr, "%s %s: %s (%s:%u, %s)\n", formattedTimeMsg.constData(),
                logLevelMsg.constData(), localMsg.constData(), context.file,
                context.line, context.function);
        fflush(stderr);
    }

    if (type == QtFatalMsg) {
        abort();
    }
}


int main(int argc, char *argv[])
{
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
    } else {
        qDebug() << "Running within IDE";
        is_in_IDE = true;
        log_to_file = false;
    }

    // Install custom log handler
    qInstallMessageHandler(customLogOutput);

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

    // NOTE: Need this right after GUI App creation
    QtWebView::initialize();
    //QtWebEngine::initialize();

    app.setWindowIcon(QIcon(":/images/logo_icon.ico"));

    QLoggingCategory::setFilterRules(QStringLiteral("qt.qml.binding.removal.info=true"));

    QQmlApplicationEngine engine;

    // -- Setup our app module which deals with QML/C++ integration
    AppModule *appModule = new AppModule(&engine);

    QString loadPage = "qrc:/lms.qml";
    loadPage = "qrc:/websockettest.qml";

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
