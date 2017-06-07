#include "cm_screengrab.h"

CM_ScreenGrab::CM_ScreenGrab(QObject *parent) :
    QObject(parent)
{
}

QPixmap CM_ScreenGrab::GrabScreen(int width, int height) {
    // Grab a screenshot of the desktop and return it
    QScreen *screen = QGuiApplication::primaryScreen();
    QPixmap pix;

    if (screen) {
        pix = screen->grabWindow(0);
    }

    if (width > 0 && height > 0) {
       // Scale the screen
        QSize size = QSize(width,height);
        pix = pix.scaled(size, Qt::KeepAspectRatio, Qt::SmoothTransformation);
    }

    return pix;
}
