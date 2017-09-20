#ifndef CM_WEBREQUEST_H
#define CM_WEBREQUEST_H

#include <QObject>
#include <QString>
#include <QEventLoop>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QHttpMultiPart>
#include <QHttpPart>
#include <QUrl>
#include <QDateTime>
#include <QFile>


class CM_WebRequest : public QObject
{
    Q_OBJECT
public:
    explicit CM_WebRequest(QObject *parent = 0);

signals:
    void progress(qint64 bytesRead, qint64 totalBytes);

public slots:
    QByteArray NetworkCall(QString url, QString method = "GET", QHash<QString, QString> *p = NULL, QHash<QString, QString> *headers = NULL, QString content_type = "text/html");
    bool DownloadFile(QString url, QString local_path);

    QString ConvertHashToQueryString(QHash<QString, QString> *arr);

    QString GetHeader(QString header_name);
    QHash<QString,QString> GetAllHeaders();

    // Download reply signals
    void downloadReadyRead();
    void downloadReplyFinished(QNetworkReply *reply);
    void downloadProgress(qint64 bytesRead, qint64 totalBytes);


private slots:
    // Network manager signals
    void httpAuthenticationRequired(QNetworkReply*,QAuthenticator *);
#ifndef QT_NO_SSL
    void httpSslErrors(QNetworkReply*,const QList<QSslError> &errors);
#endif

    // Reply signals
    void httpFinished();
    void httpReadyRead();
    void httpUpdateDataReadProgress(qint64 bytesRead, qint64 totalBytes);

private:
    QNetworkAccessManager http_manager;
    QNetworkAccessManager download_manager;
    QString download_local_path;
    QNetworkReply *http_reply;
    QNetworkReply *download_reply;
    QFile *dl_file;
    qlonglong download_size;
    qlonglong download_progress;
    QByteArray http_reply_data;
    bool http_request_active;
    bool download_active;
    qint32 num_network_calls;
    QHash<QString,QString> http_reply_headers;


};

#endif // CM_WEBREQUEST_H
