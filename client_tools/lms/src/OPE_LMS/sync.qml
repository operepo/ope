import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4
// OLD _ DON"T USE
//import com.openprisoneducation.ope 1.0

ApplicationWindow {
    visible: true
    visibility: "FullScreen"
    flags: (Qt.Window | Qt.WindowStaysOnTopHint);
    id: sync_window
    objectName: "window"
    //width: 900
    //height: 600
    title: qsTr("OPE - Learning Resource System - SYNC Tool")


    function startSyncProcess()
    {
        var r;
        progressLabel.text = "Starting sync process:";

        // Pull student information
        progressLabel.text += "\nPulling student information...";
        r = mainWidget.canvas.pullStudentInfo();
        if (r === false) { progressLabel.text += "\n  ERROR pulling student info"; }

        // Pull classes
        progressLabel.text += "\nPulling courses from canvas...";
        r = mainWidget.canvas.pullCourses();
        if (r === false) { progressLabel.text += "\n  ERROR pulling course info"; }

        progressLabel.text += "\nPulling modules for courses...";
        r = mainWidget.canvas.pullModules();
        if (r === false) { progressLabel.text += "\n  ERROR pulling module info"; }

        progressLabel.text += "\nPulling items for all courses and modules...";
        r = mainWidget.canvas.pullModuleItems();
        if (r === false) { progressLabel.text += "\n  ERROR pulling item info"; }

        progressLabel.text += "\nPulling file info for courses...";
        r = mainWidget.canvas.pullCourseFilesInfo();
        if (r === false) { progressLabel.text += "\n  ERROR pulling files info"; }

        // Don't do this unless its marked for pull
        progressLabel.text += "\nPulling file binaries...";
        r = mainWidget.canvas.pullCourseFilesBinaries();
        if (r === false) { progressLabel.text += "\n  ERROR pulling file binaries"; }

        // Pull pages for courses
        progressLabel.text += "\nPulling pages for courses...";
        r = mainWidget.canvas.pullCoursePages();
        if (r === false) { progressLabel.text += "\n  ERROR pulling pages"; }

        // Pull inbox messages for user
        progressLabel.text += "\nPulling inbox messages for user...";
        r = mainWidget.canvas.pullMessages();
        if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }

        // Pull sent messages for user
        progressLabel.text += "\nPulling sent messages for user...";
        r = mainWidget.canvas.pullMessages("sent");
        if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }

        // Mark that we have synced
        mainWidget.markAsSyncedWithCanvas();

    }


    Component.onCompleted: {

        if (mainWidget.isDebug() === true) {
            // Make sure we don't lock the screen during debugging
            console.log("WARNING! WARNING! WARNING!: Running in debug mode - secure features disabled!");
            sync_window.flags = Qt.Window;  // | Qt.WindowStaysOnTopHint;
        }

        // first see if we are credentialed
        if (mainWidget.isAppCredentialed() === false) {
            // Show error page and exit
            swipeView.setCurrentIndex(credentialErrorPage.SwipeView.index);

        }

        // Start syncing....
        startSyncProcess();
    }


    header: ToolBar
    {
        RowLayout {
            anchors.fill: parent;
            ToolButton {
                text: qsTr("Exit")
                onClicked: Qt.quit();
            }
        }

    }



    SwipeView {
        id: swipeView
        anchors.fill: parent
        currentIndex: tabBar.currentIndex

        Page {
            Label {
                id: progressLabel
                text: qsTr("Starting sync process...");
                anchors.centerIn: parent;
            }

        }

        Page {
            Label {
                text: qsTr("Second page")
                anchors.centerIn: parent
            }
        }

        Page {
            id: credentialErrorPage
            Label {
                text: qsTr("Error - App not credentialed properly. Please contact your systems administrator for help.");
                anchors.centerIn: parent;
            }
        }

//        Page {
//            WebView {
//                id: webView;
//                objectName: "testWebView"
//                anchors.fill: parent;
//                url: "http://localhost:8080";

//            }
//        }
    }

    footer: TabBar {
        id: tabBar
        currentIndex: swipeView.currentIndex
        TabButton {
            text: qsTr("First")
        }
        TabButton {
            text: qsTr("Second")
        }
        TabButton {
            text: qsTr("WebView")
        }
    }
}
