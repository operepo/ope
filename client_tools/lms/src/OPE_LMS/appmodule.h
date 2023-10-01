#ifndef APPMODULE_H
#define APPMODULE_H

#include <QObject>
#include <QDebug>
#include <QList>
#include <QCoreApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QtNetworkAuth>
#include <QOAuth2AuthorizationCodeFlow>
#include <QDesktopServices>
#include <QStandardPaths>
//#include <QtWebView>
//#include <QtWebEngine>
//#include <QWebEngineView>
//#include <QWebEnginePage>
#include <QSettings>
#include <QtConcurrent/QtConcurrent>
#include <QProcessEnvironment>

#include <QtNetwork>
#include <QNetworkAccessManager>
#include <QQmlNetworkAccessManagerFactory>
#include <QNetworkReply>
#include <QSslError>

#include <QLockFile>
#include <QAccessible>
#include <QAccessibleObject>
#include <QAccessibleWidget>
#include <QAccessibleInterface>
#include <QAccessiblePlugin>
#include <QQuickItem>
#include <QQuickWindow>

#include <QSslConfiguration>
#include <QApplication>
#include <QMessageBox>

#ifdef ANDROID
#include <QAndroidJniObject>
#include <QAndroidJniEnvironment>
#endif

#include "customlogger.h"

#include "openetworkaccessmanagerfactory.h"
#include "cm/cm_sequentialguid.h"
#include "cm/cm_httpserver.h"
#include "cm/cm_users.h"
#include "cm/cm_websockettransport.h"

#include "db.h"

#include "external/ex_canvas.h"


/**
 * Custom accessible interface - plugin for creating accessible interface, then Accessible object returned if matching
 */
//class OPECustomAccessibleItem: public QAccessibleWidget
//{
//public:
//    explicit OPECustomAccessibleItem(QQuickItem* item): QAccessibleWidget(item)
//    {

//    }
//};

//class OPECustomAccessibleFactory: public QAccessibleFac
//{
//public:
//    QAccessibleInterface *create(const QString& key, QObject* object) override
//    {
//        Q_UNUSED(key);

//        QQuickItem* item = qobject_cast<QQuickItem*>(object);
//        if (item && item->objectName() == "CustomItem") {
//            return new OPECustomAccessibleItem(item);
//        }

//        return nullptr;
//    }
//};

//QAccessibleInterface *OPEAccessibleItemFactory(const QString &classname, QObject *object) {
//    QAccessibleInterface *interface = nullptr;

//    if (classname == QLatin1String("CUSTOMOBJ") && object && object->isQuickItemType()) {
//        interface = qobject_cast<QAccessibleInterface*>(new OPECustomAccessibleItem(static_cast<QQuickItem*>(object)));
//    }
//    return interface;
//}

//void registerOPEAccessibilityComponents() {
//    QAccessible::installFactory(OPEAccessibleItemFactory);
////    QAccessible::registerAccessibleInterface([](QObject* object) {
////        QQuickItem* item = qobject_cast<QQuickItem*>(object);
////        if (item && item->objectName() == "CustomItem") {
////            return new QAccessibleQuickItem(item);
////        }

////        return nullptr;
////    });
//}

/**
 * @brief The AppModule class is the main class that runs the app.
 * It contains global values and QML interfaces
 */

class AppModule : public QObject
{
    Q_OBJECT

private:
    // Main qml engine object
    QQmlApplicationEngine *engine;

    // Lock file - to keep app from running multiple times
    QLockFile *_lf;

    // Where to store files
    QString data_path;

    // NAM Factory
    OPENetworkAccessManagerFactory *nam_factory;

    // Database object
    APP_DB *_database;

    // builtin http server
    CM_HTTPServer *server;
    quint16 HTTP_SERVER_PORT;

    // Location of the www root folder
    QString _www_root;

    // Canvas object - interface with APIs
    EX_Canvas *_canvas;
    QString _canvas_access_token;
    QString _canvas_url;

    QOAuth2AuthorizationCodeFlow canvas_auth;

    QSettings *_app_settings;
    bool exit_early;


public:

    explicit AppModule(QQmlApplicationEngine *parent = nullptr, QString program_data_path = "");
    ~AppModule();

    Q_PROPERTY(QString wwwRoot READ wwwRoot WRITE setwwwRoot NOTIFY wwwRootChanged)
    Q_PROPERTY(EX_Canvas* canvas READ canvas CONSTANT)

    bool isPermanent() { return false; }

signals:
    // notify when the root folder changes
    void wwwRootChanged();


    void canvas_authenticated();

    void showCanvasLogin(QString url);
    void canvasChanged();

public slots:
    // Print debug info
    void debugPrint(QString msg);

    // Launch a file or URL using desktop services
    bool desktopLaunch(QString url);

    // User folder where data can be stored
    QString appStudentDataFolder();
    QString appDataFolder();
    QString dataFolder();
    QString fileCacheFolder();

    // Are we debugging? Used to disable certain features during debuging
    bool isDebug();

    // Read/Write wwwRoot property
    QString wwwRoot();
    void setwwwRoot(QString wwwRoot);

    // Get the URL for the local server (e.g. http://localhost:65525)
    QString getLocalServerURL();
    // Make sure web resources are copied into place
    void copyWebResourcesToWebFolder();
    bool copyPath(QString source_path, QString dest_path);

    EX_Canvas* canvas() { return _canvas; }
    void setCanvas(EX_Canvas *c) { _canvas = c; emit canvasChanged(); }

    // === HTTP Server Functions ===
    // Start the http server
    void startServer();

    // Handle server requests
    void serverRequestArrived(CM_HTTPRequest *request,
                              CM_HTTPResponse *response);


    // === User Functions ===
    bool isAppCredentialed(); // is this app properly credentialed?
    bool hasAppSycnedWithCanvas(); // Has this app synced with the canvas server yet?
    bool markAsSyncedWithCanvas(); // Save our status as synced w canvas

    // Authenticate the user
    bool authenticateUser(QString user_name, QString password);
    bool canvasAuthenticateUser(QString user_name, QString password);
    bool isAdminUser();
    bool isFacultyUser();
    bool isStudentUser();

    // Use to lauch web browser
    void launchBrowser(const QUrl &url);


    // LMS Functions
    // Sync from the command line headless (auto sync?)
    bool syncLMSQuiet();


    void setupLoginWebView(QObject *wv);

    void sslErrorHandler(QNetworkReply *reply, QList<QSslError> errors);

    QString get_current_student_user();

    void sendAccessibilityEvent(QQuickItem *item, QAccessible::Event event_reason);

};

#endif // APPMODULE_H
