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

class CM_WebRequest : public QObject
{
    Q_OBJECT
public:
    explicit CM_WebRequest(QObject *parent = 0);

signals:

public slots:
    QString NetworkCall(QString url, QString method = "GET", QHash<QString, QString> *p = NULL, QHash<QString, QString> *headers = NULL, QString content_type = "text/html");

    QString ConvertHashToQueryString(QHash<QString, QString> *arr);

    QString GetHeader(QString header_name);
    QHash<QString,QString> GetAllHeaders();

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
    QNetworkReply *http_reply;
    QByteArray http_reply_data;
    bool http_request_active;
    qint32 num_network_calls;
    QHash<QString,QString> http_reply_headers;


};

#endif // CM_WEBREQUEST_H
