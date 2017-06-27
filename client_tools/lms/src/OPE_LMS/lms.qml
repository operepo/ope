import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4

ApplicationWindow {
    visible: true;
    visibility: "Windowed"; // "FullScreen"
    flags: (Qt.Window) ; // Qt.WindowStaysOnTopHint
    id: main_window
    objectName: "main_window"

    width: 900
    height: 600

    title: qsTr("OPE - Canvas Offline LMS")





}
