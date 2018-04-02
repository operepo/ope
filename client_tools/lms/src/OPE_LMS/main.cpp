#include <QGuiApplication>
#include <QQmlApplicationEngine>
//#include <QMessageBox>
#include <QTextCodec>
#include <QtWebView/QtWebView>
#include <QtWebEngine/qtwebengineglobal.h>

#include "openetworkaccessmanagerfactory.h"
#include "appmodule.h"

int main(int argc, char *argv[])
{
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
    QGuiApplication app(argc, argv);

    // NOTE: Need this right after GUI App creation
    QtWebView::initialize();
    QtWebEngine::initialize();

    // Set global app parameters - used by settings later
    QCoreApplication::setOrganizationName("OPE");
    QCoreApplication::setOrganizationDomain("openprisoneducation.com");
    QCoreApplication::setApplicationName("OPELMS");

    QQmlApplicationEngine engine;

    // -- Setup our app module which deals with QML/C++ integration
    AppModule *appModule = new AppModule(&engine);

    QString last_arg = QCoreApplication::arguments().last();
    bool need_sync = false;
    if (last_arg == "sync" || appModule->hasAppSycnedWithCanvas() != true)
    {
        need_sync = true;
    }

    // Set the need_sync attribute
    QQmlContext *context = engine.rootContext();
    context->setContextProperty(QStringLiteral("need_sync"), need_sync);

    //engine.load(QUrl(QLatin1String("qrc:/dropTest.qml")));
    engine.load(QUrl(QLatin1String("qrc:/main.qml")));

    return app.exec();
}
