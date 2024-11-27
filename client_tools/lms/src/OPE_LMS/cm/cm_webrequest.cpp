#include "cm_webrequest.h"

CM_WebRequest::CM_WebRequest(QObject *parent) :
    QObject(parent)
{
    // Keeps track of when a request is currently pending
    http_request_active = false;
    download_active = false;

    // DEBUG - use proxy to view http traffic - comment out for release builds
    // qDebug() << "**** DEBUG PROXY SETTINGS ACTIVE *****";
    // proxy.setType(QNetworkProxy::HttpProxy);
    // proxy.setHostName("127.0.0.1");
    // proxy.setPort(6000);
    // QNetworkProxy::setApplicationProxy(proxy);
    // export QT_LOGGING_RULES="qt.network.ssl.warning=true;qt.network.ssl.error=true;qt.network.ssl.debug=true"



    // Setup signals for the network manager
    connect(&http_manager, SIGNAL(authenticationRequired(QNetworkReply*,QAuthenticator*)),
            this, SLOT(httpAuthenticationRequired(QNetworkReply*,QAuthenticator*)));
#ifndef QT_NO_SSL
    connect(&http_manager, SIGNAL(sslErrors(QNetworkReply*,QList<QSslError>)),
            this, SLOT(httpSslErrors(QNetworkReply*,QList<QSslError>)));
#endif

}


QByteArray CM_WebRequest::NetworkCall(QString url, QString method, QHash<QString, QString> *parameters, QHash<QString, QString> *headers, QString content_type, QString post_file)
{
    // Make sure the networkmanager is set to accessible
    // NOTE - Depricated from QT6
//    QNetworkAccessManager::NetworkAccessibility n = http_manager.networkAccessible();
//    if (n != QNetworkAccessManager::Accessible) {
//        qDebug() << "NetworkCall - Network not Accessible - switching manually... " << n;
//        http_manager.setNetworkAccessible(QNetworkAccessManager::Accessible);
//    }


    // NOTE - For ordered parameters, you can use ___A_rest_of_key to preserve the parameter order.
    // e.g.  mykey would become ___B_mykey to make sure it is second.
    // ONLY WORKS FOR POST/Form-data

    // Clear current data
    http_reply_data.clear();
    http_reply_headers.clear();

    num_network_calls++;
    //QByteArray ret;

    http_request_active = true;
    bool is_upload = false;

    QString qstring = "";

    QNetworkRequest wr;

    // Make sure HTTP/1.1 keep-alives are on
    wr.setRawHeader("Connection", "Keep-Alive");

    if (content_type == "text/html" && method.toUpper() == "POST" )
    {
        // POST should default to this
        content_type = "application/x-www-form-urlencoded";
    }
    wr.setRawHeader("Content-Type", content_type.toLocal8Bit());

    if (parameters != nullptr && parameters->count() > 0 && method.toUpper() == "GET")
    {
        qstring = ConvertHashToQueryString(parameters);
        // DO Web Request
        wr.setUrl(url + "?" + qstring);
        //qDebug() << "Query String: " << qstring;
    }
    else
    {
        wr.setUrl(url);
    }
    if (parameters == nullptr) {
        parameters = new QHash<QString, QString>();
    }

    // Add the headers if they exist
    if (headers)
    {
        foreach (QString key, headers->keys())
        {
            QString item = headers->value(key);
            if (item != "")
            {
                qDebug() << "Setting Header: " << key << ": " << item;
                wr.setRawHeader(key.toLocal8Bit(), item.toLocal8Bit());
            }
        }
    }

    // Start network timeout
    qDebug() << "Starting http_timeout...";
    http_timeout.start(http_timeout_interval, this);

    if (content_type == "application/x-www-form-urlencoded" && (method.toUpper() == "POST" || method.toUpper() == "PUT"))
    {
        // Normal post with urlencoded values
        qDebug() << "Sending application/x-www-form-urlencoded...";
        QString p = ConvertHashToQueryString(parameters);
        qDebug() << "Param String: " << p;
        http_reply = http_manager.post(wr, QByteArray(p.toLocal8Bit()));
    }
    else if  (content_type == "multipart/form-data" && (method.toUpper() == "POST" || method.toUpper() == "PUT"))
    {
        qDebug() << "Multipart/Form-Data...";
        //QHttpMultiPart *parts = new QHttpMultiPart(QHttpMultiPart::MixedType);
        QHttpMultiPart *parts = new QHttpMultiPart(QHttpMultiPart::FormDataType);
        // Let it figure out its own boundary
        //parts->setBoundary(boundary.toLocal8Bit());

        // Make sure to setup a proper boundary
        QString boundary = parts->boundary(); // "-----------------------lksjfjLDSAkjfelwkjfkdjfslkjesahrAKHFD";
        // Reset the header on the web request w the boundary we will use
        wr.setHeader(QNetworkRequest::ContentTypeHeader,
                      "multipart/form-data; boundary=" + boundary);


        // ORDERED PARAMETERS
        // Copy keys to string list so we can sort
        QStringList ordered_params = parameters->keys();
        ordered_params.sort();

        // File upload post with mime headers
        // Loop through params and add a part for each
        foreach(QString key, ordered_params) {
            // Strip off the ___A_ stuff now that we are sorted
            QString final_key = key;
            if (final_key.startsWith("___")) {
                // looks like ___A_ - remove it all
                final_key = final_key.mid(6);
            }

            QHttpPart part;
            part.setHeader(QNetworkRequest::ContentDispositionHeader,
                           QVariant("form-data; name=\"" + final_key.toLocal8Bit() +"\""));
            part.setBody(parameters->value(key).toLocal8Bit());
            parts->append(part);
        }

        //QHttpPart textPart;
        //textPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("text/json")); // QVariant("form-data; name=\"text\""));
        //textPart.setHeader(QNetworkRequest::ContentTypeHeader, QVariant("text/json"));
        //textPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("form-data;"));
        //QString send = ConvertHashToQueryString(parameters);
        //textPart.setBody(send.toLocal8Bit());
        //qDebug() << "Query String: " << send;
        //parts->append(textPart);

        QFile *file_io = nullptr;
        QHttpPart file_part;
        if (post_file != "" && QFile::exists(post_file)) {
            is_upload = true;

            //wr.setAttribute(QNetworkRequest::DoNotBufferUploadDataAttribute, 1);

            // Add the file
            file_io = new QFile(post_file);
            if (!file_io->open(QIODevice::ReadOnly)) {
                qDebug() << "Failed to open file for upload: " << post_file;
                delete parts;
                return "";
            }

            QFileInfo fi = QFileInfo(post_file);

            // Set the name
            file_part.setHeader(QNetworkRequest::ContentDispositionHeader,
                                QVariant("form-data; name=\"file\"; filename=\"" + fi.fileName()  + "\""));
            //file_part.setHeader(QNetworkRequest::ContentTypeHeader,
            //                    QVariant("application/octet-stream"));
            file_part.setHeader(QNetworkRequest::ContentLengthHeader, QString::number(fi.size()));

            file_part.setBodyDevice(file_io);
            file_io->setParent(parts); // Make sure it sticks around until it is done uploading

            parts->append(file_part);
        }

        qDebug() << "Posting Parts: " << parts;
        qDebug() << "Headers: ";
        foreach(QByteArray header, wr.rawHeaderList()) {
            qDebug() << "\t" << header << ": " << wr.rawHeader(header);
        }
        //parts->dumpObjectTree();
        http_reply = http_manager.post(wr, parts);

        // Set parents that don't get deleted right away
        //if (file_part != nullptr) { file_part->setParent(http_reply); }
        //if (file_io != nullptr) { file_io->setParent(http_reply); }
        //textPart->setParent(http_reply);
        parts->setParent(http_reply);

    }
    else if (method.toUpper() == "GET")
    {
        qDebug() << "Sending GET..." << wr.url();
        http_reply = http_manager.get(wr);
    }
    else
    {
        // Unknown method?
        qDebug() << "Uknown method: " << method;
        return "";
    }


//    connect(http_reply, SIGNAL(finished()),
//            this, SLOT(httpFinished()));

    if (is_upload) {
        // -- DEAL WITH ERRORS
        connect(http_reply, SIGNAL(errorOccurred(QNetworkReply::NetworkError)),
                this, SLOT(uploadError(QNetworkReply::NetworkError)));
        // -- DEAL WITH UPLOAD EVENTS
        connect(http_reply, SIGNAL(uploadProgress(qint64,qint64)), this,
                SLOT(uploadProgress(qint64,qint64)));
    } else {
        // -- DEAL WITH ERRORS
        connect(http_reply, SIGNAL(errorOccurred(QNetworkReply::NetworkError)),
                this, SLOT(downloadError(QNetworkReply::NetworkError)));
    }

    // -- DEAL WITH DOWNLOAD EVENTS
    connect(http_reply, SIGNAL(readyRead()),
            this, SLOT(httpReadyRead()));
    connect(http_reply, SIGNAL(downloadProgress(qint64,qint64)),
            this, SLOT(httpUpdateDataReadProgress(qint64,qint64)));

    // Use a QEventLoop to allow events and block until network traffic is done
    QEventLoop loop;
    connect(http_reply, SIGNAL(finished()), &loop, SLOT(quit()));
    loop.exec(QEventLoop::ExcludeUserInputEvents);

    if (!http_reply->isFinished()) {
        qDebug() << "*** WARNING - Network Reply - finished signal but is finished is false! \n" << http_reply;
    }

    // Make sure to stop the timer
    http_timeout.stop();

    //qDebug() << "---> NETWORK CALL DONE " << url;

    // Read in the reply
    qDebug() << "NetworkCall - Got Data: " << http_reply_data;
    //ret.append(http_reply_data);
    //ret = QString::fromUtf8(http_reply_data);

    return http_reply_data;
}

bool CM_WebRequest::DownloadFile(QString url, QString local_path)
{
    bool ret = false;

    // Make sure the networkmanager is set to accessible
    // Deprecated in QT6
//    QNetworkAccessManager::NetworkAccessibility n = download_manager.networkAccessible();
//    if (n != QNetworkAccessManager::Accessible) {
//        qDebug() << "DownloadFile - Network not Accessible - switching manually... " << n;
//        download_manager.setNetworkAccessible(QNetworkAccessManager::Accessible);
//    }

    download_active = true;

    // Store our local path
    download_local_path = local_path;

    dl_file = new QFile(download_local_path);
    if(dl_file->open(QIODevice::WriteOnly))
    {
        // File opened successfully
        qDebug() << "DLFile - saving to: " << download_local_path;
    } else {
        // Unable to open the file
        qDebug() << "Unable to write to file: " << download_local_path;
        return false;
    }

    QNetworkReply *reply = download_manager.get(QNetworkRequest(QUrl(url)));
    download_reply = reply;

    download_progress = 0;
    download_size = 0;

    // Hook up our signals
    connect(reply, SIGNAL(readyRead()),
            this, SLOT(downloadReadyRead()));
    connect(reply, SIGNAL(downloadProgress(qint64,qint64)),
            this, SLOT(downloadProgress(qint64,qint64)));
    connect(&download_manager, SIGNAL(finished(QNetworkReply*)),
            this, SLOT(downloadReplyFinished(QNetworkReply*)));
    connect(reply, SIGNAL(errorOccurred(QNetworkReply::NetworkError)),
            this, SLOT(downloadError(QNetworkReply::NetworkError)));
    connect(reply, SIGNAL(sslErrors(QList<QSslError>)),
            this, SLOT(downloadSSLError(QList<QSslError>)));

    // Start the download timeout so we dont end up freezing forever on weird errors
    download_timeout.start(dl_timeout_interval, this);

    // Use a QEventLoop to allow events and block until network traffic is done
    QEventLoop loop;
    connect(reply, SIGNAL(finished()), &loop, SLOT(quit()));
    loop.exec(QEventLoop::ExcludeUserInputEvents);

    //    qDebug() << reply->header(QNetworkRequest::ContentTypeHeader).toString();
    //    qDebug() << reply->header(QNetworkRequest::LastModifiedHeader).toDateTime().toString();;
    //    qDebug() << reply->header(QNetworkRequest::ContentLengthHeader).toULongLong();
    //    qDebug() << reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
    //    qDebug() << reply->attribute(QNetworkRequest::HttpReasonPhraseAttribute).toString();

    // DL finished one way or another, turn off timer
    download_timeout.stop();

    if (reply->error()) {
        ret = false;
    } else {
        ret = true;
    }

    // Capture the download headers
    foreach(QString key, reply->rawHeaderList())
    {
        QString value = reply->rawHeader(key.toLocal8Bit());
        download_reply_headers[key] = value;
    }

    dl_file->flush();
    dl_file->close();
    delete dl_file; //dl_file->deleteLater();
    delete reply; //reply->deleteLater();
    download_active = false;

    return ret;
}

QString CM_WebRequest::ConvertHashToQueryString(QHash<QString, QString> *arr)
{
    QString ret = "";

    if (arr == nullptr) { return ret; }

    bool first = true;
    foreach (QString key , arr->keys())
    {
        QString val = arr->value(key);

        if (key ==  nullptr || key == "") { continue; }

        //if (arr->value(key) == nullptr) { *arr[key] = ""; }

        // Make sure we seperate with an &
        if (!first) { ret += "&"; }
        first = false;
        ret += QUrl::toPercentEncoding(key) + "=" + QUrl::toPercentEncoding(val);
    }

    return ret;
}

QString CM_WebRequest::GetHeader(QString header_name)
{
    return http_reply_headers[header_name];
}

QHash<QString,QString> CM_WebRequest::GetAllHeaders()
{
    return http_reply_headers;
}

QHash<QString, QString> CM_WebRequest::GetAllDownloadHeaders()
{
    return download_reply_headers;
}

int CM_WebRequest::httpStatusCode()
{
    if (http_reply == nullptr) { return 0; }

    return http_reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
}

QString CM_WebRequest::httpStatusReason()
{
    if (http_reply == nullptr) { return ""; }

    return http_reply->attribute(QNetworkRequest::HttpReasonPhraseAttribute).toString();
}

void CM_WebRequest::downloadReadyRead()
{
    // Got data - restart the timeout interval
    download_timeout.start(dl_timeout_interval, this);

    if  (!dl_file->isOpen()) {
        qDebug() << "File isn't open! " << download_local_path;
        return;
    }
    // Save this chunk of data to the dl file
    qlonglong r = dl_file->write(download_reply->readAll());
    if(r == -1) {
        // Error occured
        qDebug() << "Error writing chunk!";
        return;
    } else {
        // Read/write worked
    }
    download_progress += r;

    download_size = download_reply->header(QNetworkRequest::ContentLengthHeader).toLongLong();

    //qDebug() << "chunk saved: " << download_progress;

}

void CM_WebRequest::downloadReplyFinished(QNetworkReply *reply)
{
    // Retired this in favor of writing during readyRead to limit
    // memory size issues

    // Do something to remove warning about unused reply
    QUrl u = reply->url();

    return;
    // Deal with the downloaded file
//    if (reply->error()) {
//        qDebug() << "Error downloading file: " << reply->errorString();
//        //reply->deleteLater();
//        return;
//    }

//    qDebug() << reply->header(QNetworkRequest::ContentTypeHeader).toString();
//    qDebug() << reply->header(QNetworkRequest::LastModifiedHeader).toDateTime().toString();;
//    qDebug() << reply->header(QNetworkRequest::ContentLengthHeader).toULongLong();
//    qDebug() << reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
//    qDebug() << reply->attribute(QNetworkRequest::HttpReasonPhraseAttribute).toString();

//    QFile *dl_file = new QFile(download_local_path);
//    qDebug() << "File downloaded - saving to: " << download_local_path;
//    if(dl_file->open(QIODevice::WriteOnly))
//    {
//        dl_file->write(reply->readAll());
//        dl_file->flush();
//        dl_file->close();
//        delete dl_file;
//    }
//    reply->deleteLater();
    //    download_active = false;
}

void CM_WebRequest::downloadProgress(qint64 bytesRead, qint64 totalBytes)
{
    // Notify of download progress...
    emit progress(bytesRead, totalBytes);
}

void CM_WebRequest::downloadError(QNetworkReply::NetworkError code)
{
    try {
        qDebug() << "!!!! DLERROR - download file " << code;
        QString url = "<NO URL>";
        if (download_reply != nullptr) {
            //url = download_reply->request().url().toString();
        }
        //qDebug() << url;
    } catch(...) {
        qDebug() << "!!!!!! UNKOWN EXCEPTION - DLFile Error";
    }
    // Stop download timer
    download_timeout.stop();
}

void CM_WebRequest::downloadSSLError(const QList<QSslError> &errors)
{
    QString errorString;
    foreach (const QSslError &error, errors) {
        if (!errorString.isEmpty())
            errorString += ", ";
        errorString += error.errorString();
    }
    qDebug() << "DL File - SSL Errors: " << errorString;
    qDebug() << "DL File - Ignoring SSL Errors";
    download_reply->ignoreSslErrors();
}

void CM_WebRequest::uploadError(QNetworkReply::NetworkError code)
{
    qDebug() << "**** UPLOAD ERROR " << code;

}

void CM_WebRequest::uploadProgress(qint64 bytesSent, qint64 totalBytes)
{
    // Make sure to reset the timeout
    if (bytesSent == totalBytes) {
        // Upload done - need to give the server a few minutes to reply
        // as it may be copying the uploaded file for a minute
        http_timeout.start(60000 * 5, this);
    } else {
        http_timeout.start(http_timeout_interval, this);
    }

    //qDebug() << "uploading " << bytesSent << " / " << totalBytes;

    emit ulProgress(bytesSent, totalBytes);
}

void CM_WebRequest::uploadFinished()
{
    qDebug() << "-- Upload Finished ";

    // Turn off the timeout so we don't kill the process later
    http_timeout.stop();
}

void CM_WebRequest::timerEvent(QTimerEvent *event)
{
    if (event->timerId() == download_timeout.timerId()) {
        // Download Timer Event
        // If we got here we have been waiting too long
        qDebug() << "**** Download Timeout - stopping download";
        download_timeout.stop();
        if (download_reply->isRunning()) {
            download_reply->abort();
        }

    } else if (event->timerId() == http_timeout.timerId()) {
        // HTTP Request Timer Event
        // If we got here - waiting too long for reply/data
        qDebug() << "**** HTTP Timeout - stopping request";
        http_timeout.stop();
        if (http_reply->isRunning()) {
            http_reply->abort();
        }
    }
}

void CM_WebRequest::httpAuthenticationRequired(QNetworkReply*,QAuthenticator*)
{
    qDebug() << "Authentication requried!";
}

#ifndef QT_NO_SSL
void CM_WebRequest::httpSslErrors(QNetworkReply*,const QList<QSslError> &errors)
{
    QString errorString;
    foreach (const QSslError &error, errors) {
        if (!errorString.isEmpty())
            errorString += ", ";
        errorString += error.errorString();
    }
    qDebug() << "SSL Errors: " << errorString;
    qDebug() << "Ignoring SSL Errors";
    http_reply->ignoreSslErrors();
}
#endif


void CM_WebRequest::httpFinished()
{
    QVariant redirectionTarget = http_reply->attribute(QNetworkRequest::RedirectionTargetAttribute);

    if (http_reply->error()) {
        qDebug() << "HTTP Error: " << http_reply->errorString();
    } else if (!redirectionTarget.isNull()) {
        qDebug() << "HTTP Redirect: " << redirectionTarget;
//        QUrl newUrl = url.resolved(redirectionTarget.toUrl());
//        if (QMessageBox::question(this, tr("HTTP"),
//                                  tr("Redirect to %1 ?").arg(newUrl.toString()),
//                                  QMessageBox::Yes | QMessageBox::No) == QMessageBox::Yes) {
//            url = newUrl;
//            reply->deleteLater();
//            file->open(QIODevice::WriteOnly);
//            file->resize(0);
//            startRequest(url);
//            return;
//        }
    } else {
        //qDebug() << "Request complete: ";
//        QString fileName = QFileInfo(QUrl(urlLineEdit->text()).path()).fileName();
//        statusLabel->setText(tr("Downloaded %1 to %2.").arg(fileName).arg(QDir::currentPath()));
//        downloadButton->setEnabled(true);

    }    

//    qDebug() << "HTTP Request Complete: " << http_reply_data;

    // Make sure we use delete later for the reply object
    http_reply->deleteLater();
    http_reply = nullptr;

    http_request_active = false;
}

void CM_WebRequest::httpReadyRead()
{
    // Make sure to reset the timeout
    http_timeout.start(http_timeout_interval, this);

    // this slot gets called every time the QNetworkReply has new data.
    // We read all of its new data and write it into the file.
    // That way we use less RAM than when reading it at the finished()
    // signal of the QNetworkReply
//    if (file)
//        file->write(reply->readAll());
    //qDebug() << "ReadyRead...";
    //http_reply_data.append(http_reply->readAll());
    //QByteArray data = http_reply->readAll();
    //QString s_data = QString::fromStdString(data.toStdString());
    //http_reply_data.append(data);
    http_reply_data.append(http_reply->readAll());

    // Capture the headers
    foreach(QString key, http_reply->rawHeaderList())
    {
        QString value = http_reply->rawHeader(key.toLocal8Bit());
        http_reply_headers[key] = value;
    }

}

void CM_WebRequest::httpUpdateDataReadProgress(qint64 bytesRead, qint64 totalBytes)
{
    emit progress(bytesRead, totalBytes);
//    if (httpRequestAborted)
//        return;
    //qDebug() << "DataReadProgress: " << bytesRead << " - " << totalBytes;

}

