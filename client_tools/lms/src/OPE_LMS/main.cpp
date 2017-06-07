#include <QGuiApplication>
#include <QQmlApplicationEngine>
//#include <QtWebView>
//#include <QtWebEngine/qtwebengineglobal.h>


#include "appmodule.h"

int main(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QGuiApplication app(argc, argv);
    // NOTE: Need this right after GUI App creation
    //QtWebView::initialize();
    QtWebEngine::initialize();

    // Set global app parameters - used by settings later
    QCoreApplication::setOrganizationName("OPE");
    QCoreApplication::setOrganizationDomain("openprisoneducation.com");
    QCoreApplication::setApplicationName("OPELMS");

    QQmlApplicationEngine engine;

    // -- Setup our app module which deals with QML/C++ integration
    AppModule *appModule = new AppModule(&engine);

    engine.load(QUrl(QLatin1String("qrc:/main.qml")));

    return app.exec();
}
