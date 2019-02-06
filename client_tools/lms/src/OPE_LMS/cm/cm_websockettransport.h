#ifndef CM_WEBSOCKETTRANSPORT_H
#define CM_WEBSOCKETTRANSPORT_H

#include <QtWebChannel/QWebChannel>
#include <QtWebChannel/QWebChannelAbstractTransport>
#include <QObject>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>

// https://retifrav.github.io/blog/2018/07/14/html-from-qml-over-webchannel-websockets/


class CM_WebSocketTransport : public QWebChannelAbstractTransport
{
    Q_OBJECT

public:
    CM_WebSocketTransport();

public slots:

    void sendMessage(const QJsonObject &message) override
    {
        QJsonDocument doc(message);
        emit messageChanged(QString::fromUtf8(doc.toJson(QJsonDocument::Compact)));
    }

    void textMessageReceive(const QString &messageData)
    {
        QJsonParseError error;
        QJsonDocument message = QJsonDocument::fromJson(messageData.toUtf8(), &error);
        if (error.error)
        {
            qWarning() << "Failed to parse text message as JSON object:" << messageData
                       << "Error is:" << error.errorString();
            return;
        } else if (!message.isObject())
        {
            qWarning() << "Received JSON message that is not an object: " << messageData;
            return;
        }
        emit messageReceived(message.object(), this);
    }

signals:
    void messageChanged(const QString & message);
};

#endif // CM_WEBSOCKETTRANSPORT_H
