#ifndef CM_SCREENGRAB_H
#define CM_SCREENGRAB_H

#include <QObject>
#include <QPixmap>
#include <QScreen>
#include <QGuiApplication>

class CM_ScreenGrab : public QObject
{
    Q_OBJECT
public:
    explicit CM_ScreenGrab(QObject *parent = 0);
    
    static QPixmap GrabScreen(int width=0, int height=0);

signals:
    
public slots:
    
};

#endif // CM_SCREENGRAB_H
