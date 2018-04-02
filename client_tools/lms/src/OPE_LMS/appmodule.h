#ifndef APPMODULE_H
#define APPMODULE_H

#include <QObject>
#include <QDebug>
#include <QList>
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

#include <QNetworkAccessManager>
#include <QQmlNetworkAccessManagerFactory>
#include <QNetworkReply>
#include <QSslError>

#include <QSslConfiguration>

#ifdef ANDROID
#include <QAndroidJniObject>
#include <QAndroidJniEnvironment>
#endif

#include "openetworkaccessmanagerfactory.h"
#include "cm/cm_sequentialguid.h"
#include "cm/cm_httpserver.h"
#include "cm/cm_users.h"

#include "db.h"

#include "external/ex_canvas.h"


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

    // NAM Factory
    OPENetworkAccessManagerFactory *nam_factory;

    // Database object
    APP_DB *_database;

    // builtin http server
    CM_HTTPServer *server;

    // Location of the www root folder
    QString _www_root;

    // Canvas object - interface with APIs
    EX_Canvas *_canvas;
    QString _canvas_access_token;

    QOAuth2AuthorizationCodeFlow canvas_auth;

    QSettings *_app_settings;
    bool exit_early;


public:

    explicit AppModule(QQmlApplicationEngine *parent = 0);
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
    QString dataFolder();
    QString fileCacheFolder();

    // Are we debugging? Used to disable certain features during debuging
    bool isDebug();

    // Read/Write wwwRoot property
    QString wwwRoot();
    void setwwwRoot(QString wwwRoot);

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
    void syncLMS(QString lms);


    void setupLoginWebView(QObject *wv);

    void sslErrorHandler(QNetworkReply *reply, QList<QSslError> errors);


};

#endif // APPMODULE_H
