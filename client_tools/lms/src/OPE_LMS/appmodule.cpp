#include "appmodule.h"

AppModule::AppModule(QQmlApplicationEngine *parent) : QObject(parent)
{
    exit_early = false;

    // Settings
    //QSettings::setPath(QSettings::IniFormat, QSettings::SystemScope, QCoreApplication::organizationName() + "/" + QCoreApplication::applicationName());
    _app_settings = new QSettings(QSettings::SystemScope, QCoreApplication::organizationName(), QCoreApplication::applicationName());
    //_app_settings = new QSettings(parent);

    // Mark that we are running
    _app_settings->setValue("app/running", true);
    //_app_settings->setValue("student/canvas_access_token", "123451111");
    _canvas_access_token = _app_settings->value("student/canvas_access_token", "").toString();

    _app_settings->sync();
    //qDebug() << "App Settings: " << _app_settings->fileName();


    // Relax ssl config as we will be running through test certs
    QSslConfiguration sslconf = QSslConfiguration::defaultConfiguration();
    QList<QSslCertificate> cert_list = sslconf.caCertificates();
    QList<QSslCertificate> cert_new = QSslCertificate::fromData("CaCertificates");
    cert_list += cert_new;
    sslconf.setCaCertificates(cert_list);
    sslconf.setProtocol(QSsl::AnyProtocol);
    sslconf.setPeerVerifyMode(QSslSocket::VerifyNone);
    QSslConfiguration::setDefaultConfiguration(sslconf);

//    // Setup the custom network access policy object
//    CustomNetworkManagerFactory *factory = new CustomNetworkManagerFactory;
//    //qDebug() << factory;
//    parent->setNetworkAccessManagerFactory(factory);
//    parent->rootContext()->engine()->setNetworkAccessManagerFactory(factory);
//    //parent->networkAccessManager = NULL;
//    //qDebug() << parent->networkAccessManager();


    // Expose this object to the QML engine
    //qmlRegisterType<EX_Canvas>("com.openprisoneducation.ope", 1, 0, "Canvas");
    parent->rootContext()->setContextProperty("mainWidget", this);

    // Setup the database connection
    _database = new APP_DB(parent);
    _database->init_db();


    // Setup canvas object
    _canvas = new EX_Canvas(this, _database, _app_settings);
    _canvas->SetCanvasAccessToken(_canvas_access_token);

    // Start web server
    startServer();

}

AppModule::~AppModule()
{
    // Besure to save settings changes
    if (!exit_early) {
        _app_settings->setValue("app/running", false);
        _app_settings->sync();
        _app_settings->deleteLater();
    }

}

bool AppModule::desktopLaunch(QString url)
{
    return QDesktopServices::openUrl(QUrl(url, QUrl::TolerantMode));
}

QString AppModule::dataFolder()
{
    QDir d;
    #ifdef ANDROID
        // We want /mnt/sdcard as there should be more room on it for resources
        QAndroidJniObject mediaDir = QAndroidJniObject::callStaticObjectMethod("android/os/Environment",
                                       "getExternalStorageDirectory", "()Ljava/io/File;");
        QAndroidJniObject mediaPath = mediaDir.callObjectMethod("getAbsolutePath",
                                       "()Ljava/lang/String;");
        QString dataAbsPath = mediaPath.toString()+"/pencol/mobile_lms";
        qDebug() << "JNI-> ABS Path: " << dataAbsPath;
        QAndroidJniEnvironment env;
        if (env->ExceptionCheck())
        {
            // Handle exception if needed
            env->ExceptionClear();
        }
        d.setPath(dataAbsPath);
    #else
        d.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/content");
    #endif

    d.mkpath(d.path());

    return d.path();
}

QString AppModule::fileCacheFolder()
{
    QDir base_dir;
    base_dir.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/file_cache/");
    base_dir.mkpath(base_dir.path());
    return base_dir.path();
}

bool AppModule::isDebug()
{
    bool ret = false;

#ifdef QT_DEBUG
    ret = true;
#endif

    return ret;
}

QString AppModule::wwwRoot() {
    // Make sure www root defaults to a folder
    if (_www_root == "") {
        _www_root = dataFolder();
        QDir d(_www_root);
        d.mkpath("www_root");
        d.cd("www_root");
        _www_root = d.path();
    }
    return _www_root;
}

void AppModule::setwwwRoot(QString wwwRoot)
{
    _www_root = wwwRoot.replace("\\", "/");
    if (!_www_root.endsWith("/")) { _www_root += "/"; }
    emit wwwRootChanged();
}


/**
 * @brief AppModule::startServer
 * Start the http server
 */
void AppModule::startServer()
{
    // Turn the server on
    server = new CM_HTTPServer(this);
    QObject::connect(server,
        SIGNAL(HTTPRequestArrived(CM_HTTPRequest*,CM_HTTPResponse*)),
        this,
        SLOT(serverRequestArrived(CM_HTTPRequest*,CM_HTTPResponse*)));

    server->Start(8080);

}


/**
 * @brief AppModule::serverRequestArrived
 * Deal with server requests when they come in
 * @param request
 * @param response
 */
void AppModule::serverRequestArrived(CM_HTTPRequest *request,
                          CM_HTTPResponse *response)
{
    //qDebug() << "HTTP Request arrived: " << request->toString();

    QString url = QUrl(request->headers["URL"]).toString();

    // Deal with OAuth from Canvas
    if (url.startsWith("/oauth/response"))
    {
        qDebug() << "OAuth Response";

        _canvas->FinalizeLinkToCanvas(request, response);
        return;
    }

    // Figure out local file path for requested file
    // Remove beginning forward slash
    if (url.startsWith("/")) { url = url.mid(1); }

    QString physical_path = wwwRoot() + url;
    // Make sure all slashes are forward slashes
    physical_path = physical_path.replace("\\", "/");
    QFileInfo finfo(physical_path);
    // See if it is a real file or if we need to add the default document
    if (!finfo.isFile()) {
        // Not a file, try adding the default document (index.html)
        if (!physical_path.endsWith("/")) { physical_path += "/"; }
        physical_path += "index.html";
    }

    // === SERVE STATIC FILES ===
    finfo = QFileInfo(physical_path);
    if (!finfo.isFile()) {
        // Not a file, send 404 error
        response->RespondWith404Error(physical_path);
    } else {
        response->RespondWithFile(physical_path);
    }
}

/**
 * @brief AppModule::isAppCredentialed - Has a student logged into canvas properly yet?
 * @return true on success, false if not
 */
bool AppModule::isAppCredentialed()
{
    // Look for the canvas auth token
    bool ret = false;

    if (_canvas_access_token.length() > 10)
    {
        // If we have a token we should be good
        ret = true;
    }

    return ret;
}

bool AppModule::hasAppSycnedWithCanvas()
{
    // Check in the settings to see if we have synced yet with canvas
    bool ret = false;

    ret = _app_settings->value("app/has_synced_with_canvas", false).toBool();

    return ret;
}

bool AppModule::markAsSyncedWithCanvas()
{
    // Save our status as synced with canvas
    bool ret = true;

    _app_settings->setValue("app/has_synced_with_canvas", true);
    _app_settings->setValue("app/last_sync_with_canvas", QDateTime::currentDateTime());
    return ret;
}

bool AppModule::authenticateUser(QString user_name, QString password){
    // Try to login against local db
    bool ret = false;

    //ret = CM_Users::AuthenticateUser(user_name, password);

    if (!ret) {
        // Try to login against website
        // TODO Login against rest service on website
    }
    return ret;
}

bool AppModule::canvasAuthenticateUser(QString user_name, QString password)
{
    bool ret = false;

    // Bounce off Canvas server
    auto replyHandler = new QOAuthHttpServerReplyHandler(1337, this);
    canvas_auth.setReplyHandler(replyHandler);
    canvas_auth.setClientIdentifier("10000000000004");
    canvas_auth.setClientIdentifierSharedKey("cByuZolV0CzmfQD47UoTkXTrL36pIKo25UmE779sQXultZXCUzE086dA2UNjqNWo");

    canvas_auth.setAuthorizationUrl(QUrl("https://canvas.correctionsed.com/login/oauth2/auth"));
    canvas_auth.setAccessTokenUrl(QUrl("https://canvas.correctionsed.com/login/oauth2/token"));
    //canvas_auth.setScope("identity read");

    connect(&canvas_auth, &QOAuth2AuthorizationCodeFlow::statusChanged, [=] (
            QAbstractOAuth::Status status) {
        if (status == QAbstractOAuth::Status::Granted) {
            qDebug() << "Authenticated";
            emit canvas_authenticated();
        } else {
            qDebug() << "Not Auth! ";
        }
    });

    canvas_auth.setModifyParametersFunction([&](QAbstractOAuth::Stage stage, QVariantMap *parameters) {
        if (stage == QAbstractOAuth::Stage::RequestingAuthorization && isPermanent())
            parameters->insert("duration", "permanent");
    });

    //connect(&canvas_auth, &QOAuth2AuthorizationCodeFlow::authorizeWithBrowser,
    //        &QDesktopServices::openUrl);
    connect(&canvas_auth, &QOAuth2AuthorizationCodeFlow::authorizeWithBrowser,
                this, &AppModule::launchBrowser);

    // Start the auth process
    canvas_auth.grant();

    return ret;
}

bool AppModule::isAdminUser() {
    // TODO - lookup current user and see if it has admin
    bool ret = false;

//    if (current_user) {
//        ret = current_user->isAdminuser();
//    }
    return ret;
}

bool AppModule::isFacultyUser(){
    // TODO
    return false;
}

bool AppModule::isStudentUser() {
    // TODO
    return true;
}

void AppModule::launchBrowser(const QUrl &url)
{
    emit showCanvasLogin(url.toString());

    return;

    //QDesktopServices::openUrl(QUrl(url));
    // Have the web view display the url
    QQmlApplicationEngine *p = qobject_cast<QQmlApplicationEngine*>(this->parent());
    //QObject *wv = p->rootContext()->engine()->findChild<QObject*>("loginWebView");
    QObject *wv = p->rootObjects().first()->findChild<QObject *>("loginWebView");
    qDebug() << "First Win: " << p->findChild<QObject*>("window");
    qDebug() << "??: " << p->findChild<QObject*>("loginWebView");
    qDebug() << "first: " << p->rootObjects().first();
    //QQuickOverlay *overlay = qobject_cast<QQuickOverlay*>(p->rootObjects().first()->property("overlay"));
    //qDebug() << "Overlay: " << overlay->findChild<QObject*>("loginWebView");
    qDebug() << "Content Item: " << p->rootObjects().first()->property("overlay");
    qDebug() << "wv: " << p->rootObjects().first()->findChild<QObject*>("loginWebView");
    qDebug() << "win: " << p->rootObjects().first()->findChild<QObject*>("window");
    qDebug() << "test: " << p->rootObjects().first()->findChild<QObject*>("testWebView");
    qDebug() << "Root Objects: " << p->rootObjects().count();
p->rootObjects().first()->dumpObjectInfo();
p->rootObjects().first()->dumpObjectTree();
    //QObject *wv = p->rootContext()->rootObject()->findChild<QObject *>("loginWebView");
    if (wv) {
        wv->setProperty("url", url);
    }

}

void AppModule::syncLMS(QString lms)
{
    if (lms == "Canvas") {
        // Init Externals
        //_canvas->InitTool();
        _canvas->LinkToCanvas("http://localhost:8080/oath/response", "1");
        //_canvas->Sync();
    }
}

void AppModule::setupLoginWebView(QObject *wv)
{
    QWebEngineView *v = qobject_cast<QWebEngineView*>(wv);
    //qDebug() << " NAM: " << v->page()-
    wv->dumpObjectInfo();
    wv->dumpObjectTree();
    //QQuickWebView *w;
return;
    QObject *page = wv->property("page").value<QObject*>();
    QNetworkAccessManager *nm = page->property("networkAccessManager").value<QNetworkAccessManager*>();

    QObject::connect(nm, SIGNAL(sslErrors(QNetworkReply*, const QList<QSslError>)),
                     this, SLOT(sslErrorHandler(QNetworkReply*, const QList<QSslError>)));

    qDebug() << "||||Connected sslerrorhandler";
}

void AppModule::sslErrorHandler(QNetworkReply *reply, QList<QSslError> errors)
{
    qDebug() << "SSL Error!!!";
    reply->ignoreSslErrors(errors);
}

CustomNetworkManagerFactory::CustomNetworkManagerFactory(QObject *parent): QObject(parent)
{
    //
    qDebug() << "----Constructor - CustomNetworkManagerFactory";
}

QNetworkAccessManager *CustomNetworkManagerFactory::create(QObject *parent)
{
    qDebug() << "----CustomNetworkManagerFactory::create";
    m_networkManager = new QNetworkAccessManager(parent);
    QObject::connect(m_networkManager, SIGNAL(sslErrors(QNetworkReply*,QList<QSslError>)),
            this, SLOT(ignoreSSLErrors(QNetworkReply*,QList)));
    return m_networkManager;
}

void CustomNetworkManagerFactory::ignoreSSLErrors(QNetworkReply *reply, QList<QSslError> errors)
{
    qDebug() << "-- Ignoring Ssl errors...";
    reply->ignoreSslErrors(errors);
}
