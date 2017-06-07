#ifndef EX_CANVAS_H
#define EX_CANVAS_H

#include <QObject>
#include <QString>
#include <QJsonDocument>
#include <QJsonParseError>
#include <QJsonObject>
#include <QUrl>
#include <QDesktopServices>

#include "cm/cm_httpserver.h"
#include "cm/cm_webrequest.h"
#include "cm/cm_users.h"

class EX_Canvas : public QObject
{
    Q_OBJECT
public:
    explicit EX_Canvas(QObject *parent = 0);

    bool InitTool();

    bool LinkToCanvas(QString redirect_url, QString client_id);
    void FinalizeLinkToCanvas(CM_HTTPRequest *request, CM_HTTPResponse *response);

    bool SyncUser(QString www_root, QString user_name, QString password);

    bool SyncUserList();
    bool SyncClassList();
    bool SyncModulesList(QString class_id);
    bool SyncModuleItemsList(QString class_id, QString module_id);

    bool SyncCourse(QString course_id);

    QJsonDocument CanvasAPICall(QString api_call, QString method = "GET", QHash<QString, QString> *p = NULL);

    QString NetworkCall(QString url, QString method = "GET", QHash<QString, QString> *p = NULL, QHash<QString, QString> *headers = NULL);

private:
    QString canvas_client_id;
    QString canvas_client_secret;
    QString canvas_access_token;
    QString canvas_server;

    CM_WebRequest *web_request;

private slots:


    //// TODO
    ///
    /// File/Folder API
    /// Course API
    /// User API
    /// Accounts API
    /// Roles API
    /// Enrollments API
    /// Calendar API
    /// Assignment API
    /// Conversations API
    /// Discussions API
    /// Gradebook API
    /// Group API
    /// Module API
    /// Quizzes API
    /// Sections API
    /// Submissions API
    /// Tabs API ????
    /// WikiPages API

signals:

public slots:

};

#endif // EX_CANVAS_H
