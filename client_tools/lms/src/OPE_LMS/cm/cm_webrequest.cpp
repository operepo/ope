#include "cm_webrequest.h"

CM_WebRequest::CM_WebRequest(QObject *parent) :
    QObject(parent)
{
    // Keeps track of when a request is currently pending
    http_request_active = false;
    download_active = false;


    // Setup signals for the network manager
    connect(&http_manager, SIGNAL(authenticationRequired(QNetworkReply*,QAuthenticator*)),
            this, SLOT(httpAuthenticationRequired(QNetworkReply*,QAuthenticator*)));
#ifndef QT_NO_SSL
    connect(&http_manager, SIGNAL(sslErrors(QNetworkReply*,QList<QSslError>)),
            this, SLOT(httpSslErrors(QNetworkReply*,QList<QSslError>)));
#endif

}


QString CM_WebRequest::NetworkCall(QString url, QString method, QHash<QString, QString> *parameters, QHash<QString, QString> *headers, QString content_type)
{
    // Clear current data
    http_reply_data.clear();
    http_reply_headers.clear();

    num_network_calls++;
    QString ret;

    http_request_active = true;

    QString qstring = "";

    QNetworkRequest wr;

    if (content_type == "text/html" && method.toUpper() == "POST" )
    {
        // POST should default to this
        content_type = "application/x-www-form-urlencoded";
    }
    wr.setRawHeader("Content-Type", content_type.toLocal8Bit());

    if (parameters !=NULL && parameters->count() > 0 && method.toUpper() == "GET")
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

    // Add the headers if they exist
    if (headers)
    {
        foreach (QString key, headers->keys())
        {
            QString item = headers->value(key);
            if (item != "")
            {
                wr.setRawHeader(key.toLocal8Bit(), item.toLocal8Bit());
            }
        }
    }

    if (content_type == "application/x-www-form-urlencoded" && (method.toUpper() == "POST" || method.toUpper() == "PUT"))
    {
        // Normal post with urlencoded values
        QString p = ConvertHashToQueryString(parameters);
        qDebug() << "Param String: " << p;
        http_reply = http_manager.post(wr, QByteArray(p.toLocal8Bit()));
    }
    else if  (content_type == "multipart/form-data" && (method.toUpper() == "POST" || method.toUpper() == "PUT"))
    {
        //// TODO: Debug this???
        QHttpMultiPart *parts = new QHttpMultiPart(QHttpMultiPart::MixedType);
        // This makes parts get deleted when reply does
        parts->setParent(http_reply);
        // File upload post with mime headers
        QHttpPart textPart;
          //textPart.setHeader(QNetworkRequest::ContentDispositionHeader, QVariant("text/json")); // QVariant("form-data; name=\"text\""));
        //textPart.setHeader(QNetworkRequest::ContentTypeHeader, QVariant("text/json"));
        QString send = ConvertHashToQueryString(parameters);
        textPart.setBody(send.toLocal8Bit());
        qDebug() << "Query String: " << send;

        parts->append(textPart);
        http_reply = http_manager.post(wr, parts);

    }
    else if (method.toUpper() == "GET")
    {
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
    connect(http_reply, SIGNAL(readyRead()),
            this, SLOT(httpReadyRead()));
    connect(http_reply, SIGNAL(downloadProgress(qint64,qint64)),
            this, SLOT(httpUpdateDataReadProgress(qint64,qint64)));


    // Use a QEventLoop to allow events and block until network traffic is done
    QEventLoop loop;
    connect(http_reply, SIGNAL(finished()), &loop, SLOT(quit()));
    loop.exec(QEventLoop::ExcludeUserInputEvents);

    // Read in the reply
    //qDebug() << "NetowrkCall - Got Data: " << http_reply_data;
    ret.append(http_reply_data);

    return ret;
}

bool CM_WebRequest::DownloadFile(QString url, QString local_path)
{
    bool ret = false;

    download_active = true;

    // Store our local path
    download_local_path = local_path;

    // Hook up our signals
    connect(&download_manager, SIGNAL(readyRead()),
            this, SLOT(downloadReadyRead()));
    connect(&download_manager, SIGNAL(finished(QNetworkReply*)),
            this, SLOT(downloadReplyFinished(QNetworkReply*)));

    dl_file = new QFile(download_local_path);
    if(dl_file->open(QIODevice::WriteOnly))
    {
        // File opened successfully
        qDebug() << "File downloaded - saving to: " << download_local_path;
    } else {
        // Unable to open the file
        qDebug() << "Unable to write to file: " << download_local_path;
        return false;
    }

    QNetworkReply *reply = download_manager.get(QNetworkRequest(QUrl(url)));

    // Use a QEventLoop to allow events and block until network traffic is done
    QEventLoop loop;
    connect(reply, SIGNAL(finished()), &loop, SLOT(quit()));
    loop.exec(QEventLoop::ExcludeUserInputEvents);

    //    qDebug() << reply->header(QNetworkRequest::ContentTypeHeader).toString();
    //    qDebug() << reply->header(QNetworkRequest::LastModifiedHeader).toDateTime().toString();;
    //    qDebug() << reply->header(QNetworkRequest::ContentLengthHeader).toULongLong();
    //    qDebug() << reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
    //    qDebug() << reply->attribute(QNetworkRequest::HttpReasonPhraseAttribute).toString();


    if (reply->error()) {
        ret = false;
    } else {
        ret = true;
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

    if (arr == NULL) { return ret; }

    bool first = true;
    foreach (QString key , arr->keys())
    {
        QString val = arr->value(key);

        if (key ==  NULL || key == "") { continue; }

        //if (arr->value(key) == NULL) { *arr[key] = ""; }

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

void CM_WebRequest::downloadReadyRead()
{
    if  (!dl_file->isOpen()) {
        qDebug() << "File isn't open! " << download_local_path;
        return;
    }
    // Save this chunk of data to the dl file
    if(dl_file->write(reply->ReadAll()) == -1) {
        // Error occured
    } else {
        // Read/write worked
    }
}

void CM_WebRequest::downloadReplyFinished(QNetworkReply *reply)
{
    // Retired this in favor of writing during readyRead to limit
    // memory size issues
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

    // Make sure we use delete later for the reply object
//    http_reply->deleteLater();
//    http_reply = 0;

//    qDebug() << "HTTP Request Complete: " << http_reply_data;

    http_reply->deleteLater();
    http_reply = 0;

    http_request_active = false;
}

void CM_WebRequest::httpReadyRead()
{
    // this slot gets called every time the QNetworkReply has new data.
    // We read all of its new data and write it into the file.
    // That way we use less RAM than when reading it at the finished()
    // signal of the QNetworkReply
//    if (file)
//        file->write(reply->readAll());
    //qDebug() << "ReadyRead...";
    //http_reply_data.append(http_reply->readAll());

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
//    if (httpRequestAborted)
//        return;
    //qDebug() << "DataReadProgress: " << bytesRead << " - " << totalBytes;

}

