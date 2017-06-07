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
#include <QtWebEngine>
#include <QWebEngineView>
#include <QWebEnginePage>
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

#include "cm/cm_sequentialguid.h"
#include "cm/cm_httpserver.h"
#include "cm/cm_users.h"

#include "db.h"

#include "external/ex_canvas.h"



/**
 * @brief The CustomNetworkManagerFactory class
 * A class to deal with network manager settings within QML
 *
 */
class CustomNetworkManagerFactory: public QObject, public QQmlNetworkAccessManagerFactory
{
    Q_OBJECT
public:
    explicit CustomNetworkManagerFactory(QObject *parent = 0);
    virtual QNetworkAccessManager *create(QObject *parent);

public slots:
    void ignoreSSLErrors(QNetworkReply *reply, QList<QSslError> errors);
private:
    QNetworkAccessManager* m_networkManager;

};




/**
 * @brief The AppModule class is the main class that runs the app.
 * It contains global values and QML interfaces
 */

class AppModule : public QObject
{
    Q_OBJECT

private:
    // Database object
    APP_DB *database;

    // builtin http server
    CM_HTTPServer *server;

    // Location of the www root folder
    QString _www_root;

    // Canvas object - interface with APIs
    EX_Canvas *canvas;

    QOAuth2AuthorizationCodeFlow canvas_auth;

    QSettings _app_settings;
    bool exit_early;

public:
    explicit AppModule(QQmlApplicationEngine *parent = 0);
    ~AppModule();

    Q_PROPERTY(QString wwwRoot READ wwwRoot WRITE setwwwRoot NOTIFY wwwRootChanged)

    bool isPermanent() { return false; }

signals:
    // notify when the root folder changes
    void wwwRootChanged();


    void canvas_authenticated();

    void showCanvasLogin(QString url);

public slots:

    // User folder where data can be stored
    QString dataFolder();

    // Read/Write wwwRoot property
    QString wwwRoot();
    void setwwwRoot(QString wwwRoot);

    // === HTTP Server Functions ===
    // Start the http server
    void startServer();

    // Handle server requests
    void serverRequestArrived(CM_HTTPRequest *request,
                              CM_HTTPResponse *response);


    // === User Functions ===
    bool isAppCredentialed(); // is this app properly credentialed?

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
