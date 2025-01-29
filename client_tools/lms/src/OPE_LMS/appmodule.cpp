#include "appmodule.h"

AppModule::AppModule(QQmlApplicationEngine *parent, QString program_data_path) : QObject(parent)
{
    HTTP_SERVER_PORT = 65525;
    exit_early = false;
    engine = parent;

    //registerOPEAccessibilityComponents();

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


    nam_factory = new OPENetworkAccessManagerFactory;
    if (program_data_path == "") {
        // Get the standard program data folder to store things in.
        program_data_path = QStandardPaths::standardLocations(QStandardPaths::AppConfigLocation).at(1); // grab 2nd item
        // Remove app name (c:/programdata/ope/opelms -> c:/programdata/ope)
        program_data_path = program_data_path.replace("/OPELMS", "");
    }
    this->data_path = program_data_path;

    parent->setNetworkAccessManagerFactory(nam_factory);
    parent->rootContext()->engine()->setNetworkAccessManagerFactory(nam_factory);

    // Expose this object to the QML engine
    parent->rootContext()->setContextProperty("mainWidget", this);

    // Add our websocket transport so we can communicate with web pages in a webview
    qmlRegisterType<CM_WebSocketTransport>("cm.WebSocketTransport", 1, 0, "WebSocketTransport");

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

    // Prevent app from running twice
    QString tmp_dir = this->appStudentDataFolder(); //QDir::tempPath();
    qDebug() << tmp_dir;
    if (tmp_dir.endsWith("/student_data") == true) {
        // Should end with the current student (e.g. c:\programdata\ope\student_data\s77777) - if not, then not credentialed?
        qDebug() << "Invalid student folder! Run credential and retry." << Qt::endl;
//        QMessageBox msgbox;
//        msgbox.setText("Invalid Student Folder!");
//        msgbox.setInformativeText("Student username not detected - you must run the credential app to link this app to the student's Canvas account.");
//        msgbox.setStandardButtons(QMessageBox::Ok);
//        msgbox.exec();

        QApplication::exit(-1);
        return;
    }

    _lf = new QLockFile(tmp_dir + "/ope_lms.lock");
    if (!_lf->tryLock(100))
    {
        qDebug() << "=====================================================\n" <<
            "WARNING - App already running, exiting...\n" <<
            "only one instance allowed to run. If this is an " <<
            " error, remove the temp/ope_lms.lock file and try again" <<
            "=====================================================\n";
        out << "App already running..." << Qt::endl;
        exit_early = true;
        QApplication::exit(-1);
        return;
    }

    // Figure out the database path
    QDir d;
    d.setPath(this->appStudentDataFolder());
    d.mkpath(d.path());
    QString db_file = d.path() + "/lms.db";

    // Setup the database connection
    _database = new APP_DB(parent);
    qDebug() << "Using Database File: " << db_file;
    if (!_database->init_db(db_file)) {
        qDebug() << "FATAL ERROR - Unable to setup database! Not running in UAC mode? " << db_file;
        qDebug() << "If development, open the students home folder to grant temporary access.";
        QCoreApplication::quit();
        return;
    }

    // Start localhost web server
    startServer();

    // Copy the www resources over in a different thread
    //copyWebResourcesToWebFolder();
    // Changes for qt6
    //QFuture<void> future = QtConcurrent::run(this, &AppModule::copyWebResourcesToWebFolder);
    // Send object as the first arg
    QFuture<void> future = QtConcurrent::run(&AppModule::copyWebResourcesToWebFolder, this);

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

        //qDebug() << "Processing Course Page: " << _canvas->pullCoursePages();
        //qDebug() << "Turning In Assignments " << _canvas->pushAssignments();
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

    if (_lf) {
        _lf->unlock();
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
    //QUrl local_url = QUrl::fromUserInput("file:///" + content_folder + old_url.path(),
    //                                     content_folder, QUrl::AssumeLocalFile);
    // Fix - PDF's with # symbol #75 (https://github.com/operepo/ope/issues/75)
    // QUrl::fromLocalFile shouuld encode # as %23 - urlencoded path
    QUrl local_url = QUrl::fromLocalFile(content_folder + old_url.path());

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

QString AppModule::appStudentDataFolder()
{

    QString path = this->appDataFolder();
    QString curr_student = this->get_current_student_user();

    path += "/student_data";

    if (curr_student == "") {
        return path;
    }

    path += "/" + curr_student;

    QDir d;
    d.setPath(path);
    if (!d.exists()) {
        d.mkpath(d.path());
    }

    return path;

    /*
    // Find the appdata folder
    // NOTE - if no user set in registry (not credentialed?), then grab dir for current user.
    QString curr_student = this->get_current_student_user();
    if (curr_student == "") {
        // Return the standard path for the current logged in user.
        //QString p = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);
        QString p = this->data_path;
        QDir d;
        d.setPath(p);
        d.mkpath(d.path());
        return p + "/";
    }

    // Build the path and make sure it exists.
    QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
    QString app_data_path = env.value("Public", "c:/users/Public"); // Should be c:\\users\\Public
    if (app_data_path == "") {
        // Empty, put in a default
        app_data_path = "c:/users/Public";
    }
    app_data_path = app_data_path.replace("Public", ""); // strip off Public
    app_data_path = app_data_path + curr_student + "/AppData/Local"; // Add in current student

    // Add in the company name and app name folders
    QString org_name = QCoreApplication::organizationName();
    QString app_name = QCoreApplication::applicationName();

    if (org_name != "") {
        app_data_path += "/" + org_name;
    }
    if (app_name != "") {
        app_data_path += "/" + app_name;
    }

    QDir d;
    d.setPath(app_data_path + "/");
    // Make sure folder exists
    d.mkpath(d.path());

    return app_data_path;
    */
}

QString AppModule::appDataFolder()
{
    // Should return something like c:/programdata/ope

    // Make sure folder exists
    QDir d;
    d.setPath(data_path);
    if (!d.exists()) {
        d.mkpath(d.path());
    }

    return this->data_path;
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
        //d.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/content");
        d.setPath(this->appStudentDataFolder() + "/content");
    #endif

    if (!d.exists()) {
        d.mkpath(d.path());
    }

    return d.path();
}

QString AppModule::fileCacheFolder()
{
    QDir base_dir;
    //base_dir.setPath(QStandardPaths::writableLocation(QStandardPaths::DataLocation) + "/content/www_root/canvas_file_cache/");
    base_dir.setPath(this->appStudentDataFolder() + "/content/www_root/canvas_file_cache/");
    if (!base_dir.exists()) {
        base_dir.mkpath(base_dir.path());
    }
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

bool AppModule::authenticateUser(QString /*user_name*/, QString /*password*/){
    // Try to login against local db
    bool ret = false;

    //ret = CM_Users::AuthenticateUser(user_name, password);

    if (!ret) {
        // Try to login against website
        // TODO Login against rest service on website
    }
    return ret;
}

bool AppModule::canvasAuthenticateUser(QString /*user_name*/, QString /*password*/)
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

    //TODO - Broken from upgrade to qt6
//    canvas_auth.setModifyParametersFunction([&](QAbstractOAuth::Stage stage, QVariantMap *parameters) {
//        if (stage == QAbstractOAuth::Stage::RequestingAuthorization && isPermanent())
//            parameters->insert("duration", "permanent");
//    });

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

    /*
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
    */

}

bool AppModule::syncLMSQuiet()
{
    out << "\n\n**** Running syncLMSQuiet...\n\n";

    // Run this then quit the app0
    QCoreApplication *current_app = QCoreApplication::instance();
    if (current_app == nullptr) {
        out << "FALTAL ERROR - Couldn't find QCoreApplication instance";
        return false;
    }

    if (_canvas == nullptr) {
        out << "ERROR - No Canvas object available!";
        current_app->quit();
        return false;
    }

    QString ret;
    bool bret;
    ret = _canvas->pullStudentInfo();
    if (ret.contains("ERROR")) {
        // ERROR
        out << "ERROR - Unable to get Student Info from Canvas! " << ret;
        current_app->quit();
        return false;
    }
    out << ret;

    ret = _canvas->autoAcceptCourses();
    if (ret.contains("ERROR")) {
        // ERROR
        out << "ERROR - Unable to Accept Courses " << ret;
        current_app->quit();
        return false;
    }
    out << ret;

    ret = _canvas->pushAssignments();
    if (ret.contains("ERROR")) {
        // ERROR
        out << "ERROR - Unable to Push Assignments to Canvas " << ret;
        current_app->quit();
        return false;
    }
    out << ret;

    ret = _canvas->pullCourses();
    if (ret.contains("ERROR")) {
        // ERROR
        out << "ERROR - Unable to Pull Courses from Canvas " << ret;
        return false;
    }
    out << ret;

    bret = _canvas->pullModules();
    bret = _canvas->pullModuleItems();

    ret = _canvas->pullDiscussionTopics();
    if (ret.contains("ERROR")) {
        // ERROR
        out << "ERROR - Unable to Pull discussion topics from Canvas " << ret;
        return false;
    }
    out << ret;

//    ret = _canvas->pullQuizzes();
//    if (ret.contains("ERROR")) {
//        // ERROR
//        qDebug() << "ERROR - Unable to Pull quizzes from Canvas " << ret;
//        return false;
//    }
//    qDebug() << ret;

//    ret = _canvas->pullQuizQuestions();
//    if (ret.contains("ERROR")) {
//        // ERROR
//        qDebug() << "ERROR - Unable to Pull quiz questions from Canvas " << ret;
//        return false;
//    }
//    qDebug() << ret;


    bret = _canvas->pullCoursePages();
    bret = _canvas->pullAssignments();
    bret = _canvas->pullMessages();
    bret = _canvas->pullMessages("sent");
    bret = _canvas->pullAnnouncements();
    bret = _canvas->pullCourseFileFolders();
    bret = _canvas->pullCourseFilesInfo();
    bret = _canvas->pullSMCDocuments();
    bret = _canvas->pullCourseFilesBinaries();
    bret = _canvas->pullSMCVideos();
    bret = _canvas->updateDownloadLinks();

    // Mark that we have synced properly.
    markAsSyncedWithCanvas();

    out << "\n\n**** syncLMSQuiet - Finished!\n\n";
    current_app->quit();
    return true;
}

void AppModule::setupLoginWebView(QObject* /*wv*/)
{
    //QWebEngineView *v = qobject_cast<QWebEngineView*>(wv);
    //qDebug() << " NAM: " << v->page()-
    //wv->dumpObjectInfo();
    //wv->dumpObjectTree();
    //QQuickWebView *w;
return;
/*
    QObject *page = wv->property("page").value<QObject*>();
    QNetworkAccessManager *nm = page->property("networkAccessManager").value<QNetworkAccessManager*>();

    QObject::connect(nm, SIGNAL(sslErrors(QNetworkReply*, const QList<QSslError>)),
                     this, SLOT(sslErrorHandler(QNetworkReply*, const QList<QSslError>)));

    qDebug() << "||||Connected sslerrorhandler";
    */
}

void AppModule::sslErrorHandler(QNetworkReply *reply, QList<QSslError> errors)
{
    qDebug() << "SSL Error!!!";
    reply->ignoreSslErrors(errors);
}

QString AppModule::get_current_student_user()
{
    return _app_settings->value("student/user_name", "").toString();
}

void AppModule::sendAccessibilityEvent(QQuickItem *item, QAccessible::Event event_reason)
{
    QAccessibleEvent event(item, event_reason); // event(this, QAccessible::TextUpdated);

    //event.accessibleInterface()-(QAccessible::TextUpdated);
    //event.accessibleInterface()->setText(QAccessible::Description, QLatin1String("Hello WOrld!"));
    QAccessible::updateAccessibility(&event);


    // Find the root window so we can get the accessibility tree
//    for (QObject *o: this->engine->rootObjects()) {
//        qDebug() << "... > " << o;
//    }
//    QObject *rootObject = this->engine->rootObjects().first();
//    QQuickItem *accessible_root = nullptr;
//    //qDebug() << "RootObject: " << rootObject;
//    if (rootObject->objectName() == "appPage") {
//        // Root object IS the main window
//        accessible_root = qobject_cast<QQuickItem*>(rootObject);
//        qDebug() << "Casting: " << accessible_root;
//    } else {
//        accessible_root = rootObject->findChild<QQuickItem*>("appPage");
//    }

//    if (accessible_root == nullptr) {
//        qDebug() << "No QML object found with object_name: appPage";
//        return;
//    }

//    // Setup the update handler
//    //QAccessible::installUpdateHandler(new OPECustomAccessibleItem(item));

//    QAccessibleEvent event(this, QAccessible::Event::SoundPlayed);
//    QObject *accessible_iface = dynamic_cast<QObject *>(QAccessible::queryAccessibleInterface(item));
//    qDebug() << "Accessible Iface: " << accessible_iface;

//    QAccessibleInterface *iface = event.accessibleInterface();
//    qDebug() << "IFACe: " << iface;
//    iface->setText(QAccessible::Text::Name, QStringLiteral("Hey WOrld"));
//    QCoreApplication::sendEvent(accessible_iface, dynamic_cast<QEvent *>(&event));
//    accessible_iface->deleteLater();

//    // Send an accessibilty event from the QML system.
//    QAccessibleInterface *iface = QAccessible::queryAccessibleInterface(item);
//    //iface->item()

//    iface->setText(QAccessible::Name, "TEst 1235");

//    QString accessibleName = iface->text(QAccessible::Name);
//    qDebug() << "A Name";
//    //QAccessibleEvent event(iface, QAccessible::Focus);
//    //qDebug() << "Accessibility Event " << event;
//    QAccessibleEvent event(iface, QAccessible::NameChanged);
//    QAccessible::updateAccessibility(&event.object());

}

