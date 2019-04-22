#include "appmodule.h"

AppModule::AppModule(QQmlApplicationEngine *parent) : QObject(parent)
{
    HTTP_SERVER_PORT = 65525;
    exit_early = false;
    engine = parent;
    nam_factory = new OPENetworkAccessManagerFactory;

    parent->setNetworkAccessManagerFactory(nam_factory);
    parent->rootContext()->engine()->setNetworkAccessManagerFactory(nam_factory);

    //QObject *root = engine->rootObjects().first();
    //root->setParent("networkAccess", parent->networkAccessManager());

    // Connect the SSL errors to our handler
    //QNetworkAccessManager *nam = parent->networkAccessManager();
    //qDebug() << "Current nam " << nam;
    //qDebug() << "Current signals " << nam-
    //QObject::connect(nam, SIGNAL(sslErrors(QNetworkReply*,QList<QSslError>)),
    //        this, SLOT(sslErrorHandler(QNetworkReply*,QList<QSslError>)));


    // Settings
    //QSettings::setPath(QSettings::IniFormat, QSettings::SystemScope, QCoreApplication::organizationName() + "/" + QCoreApplication::applicationName());
    _app_settings = new QSettings(QSettings::SystemScope, QCoreApplication::organizationName(), QCoreApplication::applicationName());
    // --------NOTE - We use KEY_WOW64_64KEY registry location - other apps need to use the same to find values
    //_app_settings = new QSettings("HKEY_LOCAL_MACHINE\\Software\\OPE\\OPELMS");
    //_app_settings = new QSettings(parent);

    // Mark that we are running
    _app_settings->setValue("app/running", true);
    //_app_settings->setValue("student/canvas_access_token", "123451111");
    _canvas_access_token = _app_settings->value("student/canvas_access_token", "").toString();
    _canvas_url = _app_settings->value("student/canvas_url", "https://canvas.ed").toString();

    _app_settings->sync();
    //qDebug() << "App Settings: " << _app_settings->fileName();


    // Expose this object to the QML engine
    //qmlRegisterType<EX_Canvas>("com.openprisoneducation.ope", 1, 0, "Canvas");
    parent->rootContext()->setContextProperty("mainWidget", this);

    // Add our websocket transport so we can communicate with web pages in a webview
    qmlRegisterType<CM_WebSocketTransport>("cm.WebSocketTransport", 1, 0, "WebSocketTransport");

    // Setup the database connection
    _database = new APP_DB(parent);
    _database->init_db();

    // Start localhost web server
    startServer();

    // Copy the www resources over in a different thread
    //copyWebResourcesToWebFolder();
    QFuture<void> future = QtConcurrent::run(this, &AppModule::copyWebResourcesToWebFolder);

    // Setup canvas object
    _canvas = new EX_Canvas(this, _database, _app_settings, getLocalServerURL());
    _canvas->SetCanvasAccessToken(_canvas_access_token);
    _canvas->SetCanvasURL(_canvas_url);

    QByteArray envVar = qgetenv("QTDIR");
    if (envVar.isEmpty()) {
        // Running outside IDE
    } else {
        // Running INSIDE IDE (Debug!)
        // DEBUG
        // Run some tests on the process video/smc/docs code
        //qDebug() << _canvas->ProcessSMCVideos("<iframe width=\"650\" height=\"405\" src=\"https://smc.ed/media/player.load/6bc33efb174248c5bfff9cdd5f986ae9?autoplay=true\" frameborder=\"0\" allowfullscreen></iframe>");

        //qDebug() << _canvas->ProcessSMCDocuments("<iframe src=\"https://smc.ed/smc/static/ViewerJS/index.html#/media/dl_document/2c4ed3d973b443fd930159764dc60ef7\" width=\"734\" height=\"620\" allowfullscreen=\"allowfullscreen\" webkitallowfullscreen=\"webkitallowfullscreen\"></iframe>");

        //qDebug() << "Pulling SMC Videos " << _canvas->pullSMCVideos();

        qDebug() << "Processing Course Page: " << _canvas->pullCoursePages();
        qDebug() << "Turning In Assignments " << _canvas->pushAssignments();
    }

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

void AppModule::debugPrint(QString msg)
{
    if (msg.length() > 0) { qDebug() << msg; }

    QList<QNetworkAccessManager *> all_nams = engine->findChildren<QNetworkAccessManager *>();
    qDebug() << "-- NAMS " << all_nams;

    //all_nams = engine->rootObjects()->findChildren<QNetworkAccessManager*>();
    QList<QObject*> objs = engine->rootObjects();
    foreach (QObject *o , objs) {
        qDebug() << "--- Root Object " << o;
        qDebug() << "------ Children " << o->findChildren<QNetworkAccessManager*>();
    }

}

bool AppModule::desktopLaunch(QString url)
{
    bool ret = false;

    // Decide if this is a local file or not?
    qDebug() << "Deciding if its ok to open " << url;

    QString content_folder = dataFolder() + "/www_root/";

    // Strip off the http and host info
    QUrl old_url = QUrl::fromUserInput(url);
    if (!old_url.isValid()) {
        qDebug() << "Invalid URL - canceling open " << url;
        return false;
    }

    // Make a new local file url
    QUrl local_url = QUrl::fromUserInput("file:///" + content_folder + old_url.path(),
                                         content_folder, QUrl::AssumeLocalFile);

    qDebug() << " >>>>> " << local_url << " - " << local_url.toLocalFile();

    if (local_url.isValid() && QFile::exists(local_url.toLocalFile())) {
        qDebug() << "Got valid local url: " << local_url;
        try {
            QDesktopServices::openUrl(local_url);
            qDebug() << "url opened " << local_url;
        } catch(...) {
            qDebug() << "Error opening url " << local_url;
        }

        ret = true;
    } else {
        qDebug() << "Invalid URL or file doesn't exist! " << local_url;
        ret = false;
    }

    return ret;
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
    base_dir.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/content/www_root/canvas_file_cache/");
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

QString AppModule::getLocalServerURL()
{
    return "http://localhost:" + QString::number(server->getHTTPPort());
}

void AppModule::copyWebResourcesToWebFolder()
{
    // Get app folder
    QString source_path = QCoreApplication::applicationDirPath();
    source_path = QDir::cleanPath(source_path + "/web_content");

    // Get www_folder
    QString dest_path = wwwRoot();

    qDebug() << "Copying web content: " << source_path << " --> " << dest_path;

    // Copy the qwebchannel.js file
    //QFileInfo jsFileInfo(dest_path + "/qwebchannel.js");
    //if (!jsFileInfo.exists()) {
    // Always make a fresh copy
    //QFile::copy(":/qwebchannel.js", jsFileInfo.absoluteFilePath());
    //}

    // Copy web_content folder
    if (!copyPath(source_path, dest_path)) {
        qDebug() << "Error copying files to web folder";
        return;
    }
    qDebug() << "COPY WEB CONTENT DONE";
}

bool AppModule::copyPath(QString source_path, QString dest_path)
{
    QDir source_dir = QDir(source_path);
    if (!source_dir.exists()) {
        qDebug() << "Source dir doesn't exist " << source_path;
        return false;
    }

    QDir dest_dir = QDir(dest_path);
    if (!dest_dir.exists()) {
        qDebug() << "Making dir " << dest_path;
        dest_dir.mkpath(dest_path);
    }

    // Make folders
    foreach(QString dirname, source_dir.entryList(QDir::Dirs | QDir::NoDotAndDotDot)) {
        QString new_source_path = source_path + "/" + dirname;
        QString new_dest_path = dest_path + "/" + dirname;
        //qDebug() << "Making Dir " << new_dest_path;
        dest_dir.mkpath(new_dest_path);
        copyPath(new_source_path, new_dest_path);
    }

    // Copy files
    foreach(QString fname, source_dir.entryList(QDir::Files)) {
        QString source_file_path = source_path + "/" + fname;
        QString dest_file_path = dest_path + "/" + fname;
        //qDebug() << "Copying file " << source_file_path << " -- > " << dest_file_path;
        // Remove the old file to force a copy
        if (QFile::exists(dest_file_path)) {
            QFile::remove(dest_file_path);
        }
        // Copy file into place
        QFile::copy(source_file_path, dest_file_path);

    }

    return true;
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

    server->Start(HTTP_SERVER_PORT);

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

    QUrl url = QUrl(request->headers["URL"]);

    // Deal with OAuth from Canvas
    if (url.path().startsWith("/oauth/response"))
    {
        qDebug() << "OAuth Response";

        _canvas->FinalizeLinkToCanvas(request, response);
        return;
    }

    // Figure out local file path for requested file
    // Remove beginning forward slash
    qDebug() << "Req for URL: " << url;
    // Does this end with /? Might need to add index.html?
    //if (url.path().endsWith("/")) { url += "index.html"; }

    QString physical_path = QDir::cleanPath(wwwRoot() + url.path(QUrl::FullyDecoded));
    // Make sure all slashes are forward slashes
    //physical_path = physical_path.replace("\\", "/");
    QFileInfo finfo(physical_path);

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
    //QWebEngineView *v = qobject_cast<QWebEngineView*>(wv);
    //qDebug() << " NAM: " << v->page()-
    //wv->dumpObjectInfo();
    //wv->dumpObjectTree();
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

