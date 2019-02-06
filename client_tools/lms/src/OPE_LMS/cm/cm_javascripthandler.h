#ifndef CM_JAVASCRIPTHANDLER_H
#define CM_JAVASCRIPTHANDLER_H

#include <QObject>

// Deal with javascript clicks/interactions on webview
// Idea from https://austingwalters.com/returning-and-storing-user-selected-web-elements-from-qt-webview/

class CM_JavaScriptHandler : public QObject
{
    Q_OBJECT
public:
    explicit CM_JavaScriptHandler(QObject *parent = nullptr);

    void injectJavaScriptHandler(QString web_view_id);

signals:

public slots:
};

#endif // CM_JAVASCRIPTHANDLER_H
