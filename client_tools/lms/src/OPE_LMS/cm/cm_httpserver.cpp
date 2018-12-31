#include "cm_httpserver.h"

namespace cm_pem_certs {
char pemdata_cert[] =
        "-----BEGIN CERTIFICATE-----\n"
        "MIICeTCCAeKgAwIBAgIRAKKKnOj6Aarmwf0phApitVAwDQYJKoZIhvcNAQEFBQAw\n"
        "ODELMAkGA1UEBhMCVVMxFDASBgNVBAoTC0V4YW1wbGUgT3JnMRMwEQYDVQQDEwpF\n"
        "eGFtcGxlIENBMB4XDTA2MDMxNTA3MDU1MloXDTA3MDMxNTA3MDU1MlowOjEVMBMG\n"
        "A1UEAxMMRXhhbXBsZSBVc2VyMQswCQYDVQQGEwJVUzEUMBIGA1UEChMLRXhhbXBs\n"
        "ZSBPcmcwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAPkKn0FfHMvRZv+3uFcw\n"
        "VrOadJmANzLVeVW/DHZp4CXokXSksM66ZMqFuQRBk5rnIZZpZmVp1tTRDVt9sEAY\n"
        "YNa8CRM4HXkVlU0lCKdey18CSq2VuSvNtw8dDpoBmQt3nr9tePvKHnpS3nm6YjR2\n"
        "NEvIKt1P4mHzYXLmwoF24C1bAgMBAAGjgYAwfjAdBgNVHQ4EFgQUmQIdzyDaPYWF\n"
        "fPJ8PPOOm1eSsucwHwYDVR0jBBgwFoAUkCglAizTO7iqwLeaO6r/8kJuqhMwDAYD\n"
        "VR0TAQH/BAIwADAeBgNVHREEFzAVgRNleGFtcGxlQGV4YW1wbGUuY29tMA4GA1Ud\n"
        "DwEB/wQEAwIF4DANBgkqhkiG9w0BAQUFAAOBgQAuhbiUgy2a++EUccaonID7eTJZ\n"
        "F3D5qXMqUpQxlYxU8du+9AxDD7nFxTMkQC2pzfmEc1znRNmJ1ZeLRL72VYsVndcT\n"
        "psyM8ABkvPp1d2jWIyccVjGpt+/RN5IPKm/YIbtIZcywvWuXrOp1lanVmppLfPnO\n"
        "6yneBkC9iqjOv/+Q+A==\n"
        "-----END CERTIFICATE-----\n";

char pemdata_privkey[] =
        "-----BEGIN PRIVATE KEY-----\n"
        "MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAPkKn0FfHMvRZv+3\n"
        "uFcwVrOadJmANzLVeVW/DHZp4CXokXSksM66ZMqFuQRBk5rnIZZpZmVp1tTRDVt9\n"
        "sEAYYNa8CRM4HXkVlU0lCKdey18CSq2VuSvNtw8dDpoBmQt3nr9tePvKHnpS3nm6\n"
        "YjR2NEvIKt1P4mHzYXLmwoF24C1bAgMBAAECgYEAyIjJHDaeVXDU42zovyxpZE4n\n"
        "PcOEryY+gdFJE8DFgUD4f1huFsj4iCuNg+PaG42p+hf9IARNvSho/RcEaVg4AJrV\n"
        "jRP8r7fSqcIGr6lGuvDFFv3SU5ddy84g5oqLYGKvuPSHMGfVsZSxAwOrzD4bH19L\n"
        "SNqtNcpdBsBd7ZiEE4ECQQD/oJGui9D5Dx3QVcS+QV4F8wuyN9jYIANmX/17o0fl\n"
        "BL0bwRU4RICwadrcybi5N0JQLIYSUm2HGqNvAJbtnuQxAkEA+WeYLLYPeawcy+WU\n"
        "kGcOR7BUjHiG71+6cvU4XIDW2bezA04fqWXkZRFAwHTMpQb785/XalFftgS21kql\n"
        "8yLDSwJAHkeT2hwftdDPlEUEmBDAJW5DvWmWGwu3u2G1cfbGZl9oUyhM7ixXHg57\n"
        "6VlPs0jTZxHPE86FwNIr99MXDbCbkQJBAMDFOJK+ecGirXNP1P+0GA6DFSap9inJ\n"
        "BRTbwx+EmgwX966DUOefEOSpbDIVVSPs/Qr2LgtIMEFA7Y0+j3wZD3cCQBsTwccd\n"
        "ASQx59xakpq11eOlTYz14rjwodr4QMyj26WxEPJtz7hKokx/+EH6fWuPIUSrROM5\n"
        "07y2gaVbYxtis0s=\n"
        "-----END PRIVATE KEY-----\n";

char pemdata_cacert[] =
        "";

} // End of namespace


CM_HTTPServer::CM_HTTPServer(QObject *parent) :
    QTcpServer(parent)
{
    http_port = 80;
    ssl_on = false;
    disabled = false;

#ifndef CM_DISABLE_SSL
    setSSLCert(cm_pem_certs::pemdata_cert);
    setSSLKey(cm_pem_certs::pemdata_privkey);
    setCACert(cm_pem_certs::pemdata_cacert);
#endif

    bytesRead = 0;
    bytesWritten = 0;
    encryptedBytesRead = 0;
    encryptedBytesWritten = 0;
}

bool CM_HTTPServer::Start(quint16 port, bool use_ssl)
{
    // Start the server listening for connections
    http_port = port;
    ssl_on = use_ssl;

    listen(QHostAddress::Any, port);

    return true;
}

quint16 CM_HTTPServer::getHTTPPort()
{
    return http_port;
}

bool CM_HTTPServer::registerPathHandler(QString path, qintptr handler)
{
    bool ret = false;
 ////TODO
    return ret;
}

bool CM_HTTPServer::registerExtentionHandler(QString extention, qintptr handler)
{
    bool ret = false;
    ////TODO
    return ret;
}

bool CM_HTTPServer::registerHandler(qintptr handler)
{
    bool ret = false;
    ////TODO
    return ret;
}

void CM_HTTPServer::incomingConnection(qintptr socket)
{
    if (disabled)
         return;

 // When a new client connects, the server constructs a QTcpSocket and all
 // communication with the client is done over this QTcpSocket. QTcpSocket
 // works asynchronously, this means that all the communication is done
 // in the two slots readClient() and discardClient().

    if (ssl_on) {
#ifndef CM_DISABLE_SSL
        QSslSocket *s = new QSslSocket(this);
        s->setSocketDescriptor(socket);

        // Setup Signals/Slots for the socket
        connect(s, SIGNAL(aboutToClose()), this, SLOT(slot_clientAboutToClose()));
        connect(s, SIGNAL(bytesWritten(qint64)), this, SLOT(slot_clientBytesWritten(qint64)));
        connect(s, SIGNAL(connected()), this, SLOT(slot_clientConnected()));
        connect(s, SIGNAL(destroyed()), this, SLOT(slot_clientDestroyed()));
        connect(s, SIGNAL(destroyed(QObject*)), this, SLOT(slot_clientDestroyed(QObject*)));
        connect(s, SIGNAL(disconnected()), this, SLOT(slot_clientDisconnected()));
        connect(s, SIGNAL(encrypted()), this, SLOT(slot_clientEncrypted()));
        connect(s, SIGNAL(encryptedBytesWritten(qint64)), this, SLOT(slot_clientEncryptedBytesWritten(qint64)));
        connect(s, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(slot_clientError(QAbstractSocket::SocketError)));
        connect(s, SIGNAL(hostFound()), this, SLOT(slot_clientHostFound()));
        connect(s, SIGNAL(modeChanged(QSslSocket::SslMode)), this, SLOT(slot_clientModeChanged(QSslSocket::SslMode)));
        // Not available??
        //connect(s, SIGNAL(objectNameChanged(QString,QPrivateSignal)), this, SLOT(slot_clientObjectNameChanged(QString, QPrivateSignal)));
        connect(s, SIGNAL(peerVerifyError(QSslError)), this, SLOT(slot_clientPeerVerifyError(QSslError)));
        connect(s, SIGNAL(proxyAuthenticationRequired(QNetworkProxy,QAuthenticator*)), this, SLOT(slot_clientProxyAuthenticationRequest(QNetworkProxy, QAuthenticator*)));
        connect(s, SIGNAL(readChannelFinished()), this, SLOT(slot_clientReadChannelFinished()));
        connect(s, SIGNAL(readyRead()), this, SLOT(slot_clientReadyRead()));
        connect(s, SIGNAL(sslErrors(QList<QSslError>)), this, SLOT(slot_clientSslErrors(QList<QSslError>)));
        connect(s, SIGNAL(stateChanged(QAbstractSocket::SocketState)), this, SLOT(slot_clientStateChanged(QAbstractSocket::SocketState)));

        // Set the server cert/key
        // Set CA Cert on each socket during connection too
        s->addDefaultCaCertificate(ca_cert);
        s->setLocalCertificate(server_cert);
        s->setPrivateKey(server_key);
        //s->setPeerVerifyMode(QSslSocket::VerifyNone);

        // Some SSL Options for tuning security/connections
        //s->setCiphers(QSslSocket::supportedCiphers());
        //s->setProtocol(QSsl::AnyProtocol);
        //s->ignoreSslErrors();
        //s->setPeerVerifyMode(QSslSocket::VerifyNone);

        // Have the server start the handshake
        s->startServerEncryption();
        //qDebug() << "New SSL Connection: " << s ;
#endif
    } else {
        // Non SSL Socket
        QTcpSocket* s = new QTcpSocket(this);
        s->setSocketDescriptor(socket);

        // Setup the signals/slots tcp socket
        connect(s, SIGNAL(aboutToClose()), this, SLOT(slot_clientAboutToClose()));
        connect(s, SIGNAL(bytesWritten(qint64)), this, SLOT(slot_clientBytesWritten(qint64)));
        connect(s, SIGNAL(connected()), this, SLOT(slot_clientConnected()));
        connect(s, SIGNAL(destroyed()), this, SLOT(slot_clientDestroyed()));
        connect(s, SIGNAL(destroyed(QObject*)), this, SLOT(slot_clientDestroyed(QObject*)));
        connect(s, SIGNAL(disconnected()), this, SLOT(slot_clientDisconnected()));
        connect(s, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(slot_clientError(QAbstractSocket::SocketError)));
        connect(s, SIGNAL(hostFound()), this, SLOT(slot_clientHostFound()));
        //connect(s, SIGNAL(objectNameChanged(QString,QPrivateSignal)), this, SLOT(slot_clientObjectNameChanged(QString, QPrivateSignal)));
        connect(s, SIGNAL(proxyAuthenticationRequired(QNetworkProxy,QAuthenticator*)), this, SLOT(slot_clientProxyAuthenticationRequest(QNetworkProxy, QAuthenticator*)));
        connect(s, SIGNAL(readChannelFinished()), this, SLOT(slot_clientReadChannelFinished()));
        connect(s, SIGNAL(readyRead()), this, SLOT(slot_clientReadyRead()));
        connect(s, SIGNAL(stateChanged(QAbstractSocket::SocketState)), this, SLOT(slot_clientStateChanged(QAbstractSocket::SocketState)));

        qDebug() << "New Non SSL Connection: " << s;
    }
}

// Set SSL Certs
#ifndef CM_DISABLE_SSL
void CM_HTTPServer::setCACert(char pem_data[])
{
    // Remove old CA Certs
    ca_certs.clear();

    // Split the cabundle into individual certs and load each of them seperately
    QString d = pem_data;
    QStringList parts = d.split("-----END CERTIFICATE-----");
    foreach(QString p, parts)
    {
        if (p.trimmed().length() > 0) {
            // Add the end cert line back on
            p+="-----END CERTIFICATE-----\n";
            //qDebug() << "Cert Found: " << p;
            QByteArray ba;
            ba.append(p);
            ca_certs += QSslCertificate(ba, QSsl::Pem);
        }
    }

    // Set the CA cert globally and on each client socket during connection
    QSslSocket::setDefaultCaCertificates(ca_certs);
    ca_cert = QSslCertificate(pem_data, QSsl::Pem);
}
#endif

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::setSSLCert(char pem_data[])
{
    server_cert = QSslCertificate(pem_data, QSsl::Pem);
}
#endif

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::setSSLKey(char pem_data[])
{
    server_key = QSslKey(pem_data, QSsl::Rsa, QSsl::Pem, QSsl::PrivateKey );
}
#endif

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::setSSLCert(char ca_data[], char cert_data[], char key_data[])
{
    setCACert(ca_data);
    setSSLCert(cert_data);
    setSSLKey(key_data);
}
#endif

// Client Socket Signals
void CM_HTTPServer::slot_clientAboutToClose()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_ClientAboutToClose: " << s;
}

void CM_HTTPServer::slot_clientBytesWritten(qint64 bytes)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    bytesWritten+=bytes;
    //CM_HTTPServer::totalBytesWritten+=bytes;
    //qDebug() << "slot_clientBytesWritten: " << s << " - " << bytes;
}

void CM_HTTPServer::slot_clientConnected()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientConnected: " << s;
}

void CM_HTTPServer::slot_clientDestroyed()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientDestroyed: " << s;
}

void CM_HTTPServer::slot_clientDestroyed(QObject*)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientDestroyed *: " << s;
}

void CM_HTTPServer::slot_clientDisconnected()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientDisconnected: " << s;
    s->deleteLater();
}

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::slot_clientEncrypted()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientEncrypted: " << s;
}
#endif

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::slot_clientEncryptedBytesWritten(qint64 bytes)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    encryptedBytesWritten += bytes;
    //qDebug() << "slot_clientEncryptedBytesWritten: " << s << " - " << bytes;
}
#endif

void CM_HTTPServer::slot_clientError(QAbstractSocket::SocketError error)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientError: " << s;
    //qDebug() << "\t" << error;
}

void CM_HTTPServer::slot_clientHostFound()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientHostFount: " << s;
}

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::slot_clientModeChanged(QSslSocket::SslMode mode)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientModeChanged: " << s;
    //qDebug() << "\t" << mode;
}
#endif

void CM_HTTPServer::slot_clientObjectNameChanged(QString name, QPrivateSignal)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientObjectNameChanged: " << s;
    //qDebug() << "\t" << name;
}

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::slot_clientPeerVerifyError(QSslError error)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientPeerVerifyError: " << s;
    //qDebug() << "\t" << error;
}
#endif

void CM_HTTPServer::slot_clientProxyAuthenticationRequest(QNetworkProxy proxy, QAuthenticator *auth)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientProxyAuthenticationRequest: " << s;
    //qDebug() << "\t" << proxy << " - " << auth;
}

void CM_HTTPServer::slot_clientReadChannelFinished()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientReadChannelFinished: " << s;
}

void CM_HTTPServer::slot_clientReadyRead()
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientReadyRead: " << s;
    if (disabled)
         return;

    // This slot is called when the client sent data to the server. The
    // server looks if it was a get request and sends a very simple HTML
    // document back.
    QByteArray p_data;
    while (s->bytesAvailable() > 0) {
        p_data.append(s->readAll());
    }

    QString packet = QString(p_data);

    CM_HTTPRequest *req = new CM_HTTPRequest(this);
    req->ParsePacket(packet);
    CM_HTTPResponse *resp = new CM_HTTPResponse(this);

    // Use HTTP/1.1 if it is requested
    resp->SetProtocol(req->GetProtocol());

    emit HTTPRequestArrived(req, resp);

    // Send back the response to the client
    s->write(resp->GetResponse());
    //qDebug() << "Wrote HTTP Response: " << resp->toString();
    s->flush();

    // Close if protocol is HTTP/1.0
    if (req->headers["Protocol"] == "HTTP/1.0") { s->close(); }
    //s->close();

}

#ifndef CM_DISABLE_SSL
void CM_HTTPServer::slot_clientSslErrors(QList<QSslError> errors)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientSslErrors: " << s;
    //qDebug() << "SSL Error!" << errors.first().errorString();
}
#endif

void CM_HTTPServer::slot_clientStateChanged(QAbstractSocket::SocketState state)
{
    QTcpSocket *s = (QTcpSocket *)sender();
    //qDebug() << "slot_clientStateChanged" << s;
    //qDebug() << "\t" << state;
}



// HTTPRequest Functions
CM_HTTPRequest::CM_HTTPRequest(QObject *parent) :
    QObject(parent)
{

}

void CM_HTTPRequest::ParsePacket(QString packet)
{
    // Parse the packet and split the headers and body of the request
    QStringList parts = packet.split("\r\n\r\n");
    if (parts.length() < 2)
    {
        // Invalid HTTP request? need at least a header and a body
        //qDebug() << "Invalid packet recieved: \n\t" << packet;

    }

    QStringList header_lines = parts[0].split("\r\n");
    headers.clear();

    // Special parsing for the first line
    if (header_lines.length() > 0)
    {
        QString line = header_lines[0];
        QStringList p = line.split(" ");
        if (p.length() >= 3) {
            // First item is method GET/POST/PUT/DELET/...etc
            headers["Method"] = p[0].trimmed();
            // Last item is HTTP/1.0 or HTTP/1.1 (protocol)
            headers["Protocol"] = p[p.count()-1].trimmed();

            // Grab everything in between for the URL
            QString curr_url = "";
            int start_part = 1;
            int end_part = p.count() - 2;
            for(int i=start_part; i<=end_part; i++)
            {
                if (curr_url != "") { curr_url += " "; }
                curr_url += p[i];
            }
            headers["URL"] = curr_url;
            url = QUrl(curr_url);

        }
    }

    // Store the headers
    foreach (QString line, header_lines)
    {
        QStringList p = line.split(":");
        if (p.length() < 2) { continue; }
        headers[p[0]] = p[1].trimmed();
    }

    // Combine the rest of the parts in case the body got split too (if it had double line feeds in it)
    body = "";
    for(int i=1; i<parts.length(); i++)
    {
        body.append(parts[i]);
    }

    //qDebug() << "Packet Recieved: \n\t" << this->toString();
}

QString CM_HTTPRequest::toString()
{
    QString str = "Test";
    QJsonObject obj;

    foreach(QString key, headers.keys()) {
        obj[key] = headers[key];
    }

    QJsonDocument doc;
    doc.setObject(obj);

    return doc.toJson();
}


/// CM_HTTPResponse Functions
///
CM_HTTPResponse::CM_HTTPResponse(QObject *parent) :
    QObject(parent)
{

}

QString CM_HTTPResponse::toString()
{
    QString str = "Test";
    QJsonObject obj;

    foreach(QString key, headers.keys()) {
        obj[key] = headers[key];
    }

    QJsonDocument doc;
    doc.setObject(obj);

    return doc.toJson();
}

QByteArray CM_HTTPResponse::GetResponse()
{
    QString ret = "";

    if (response_result["Protocol"] == "") { response_result["Protocol"] = "HTTP/1.0"; };
    if (response_result["CODE"] == "") { response_result["CODE"] = "200"; };
    if (response_result["Message"] == "") { response_result["Message"] = "Ok"; };

    // Make sure we have a Content-Type and Content-Length header
    if (headers["Content-Type"] == "") { headers["Content-Type"] = "text/html"; }

    QVariant len = body.length();
    if (headers["Content-Length"] == "") { headers["Content-Length"] = len.toString(); }

    // If HTTP/1.0 then set the Connection: close header
    if (response_result["Protocol"] == "HTTP/1.0") { headers["Connection"] = "close"; }

    ret = response_result["Protocol"] + " " + response_result["CODE"] + " " + response_result["Message"] + "\n";
    foreach(QString key, headers.keys()) {
        ret += key + ": " + headers[key] + "\n";
    }
    ret += "\n";
    //ret += body;

    QByteArray arr = ret.toUtf8().constData();

    arr.append(body);

    return arr;
}
