import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.3
import QtQuick.Controls.Universal 2.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    id: syncPage
    anchors.fill: parent

    Connections {
        target: mainWidget.canvas;
        onProgress: {
            //console.log("dl progress called");
            progressCurrentItem.text = currentItem;

            if (totalBytes == 0) {
                syncProgress.value = 0

            } else {
                syncProgress.value = bytesRead / totalBytes;
            }
        }
    }

    function startSyncProcess()
    {
        var r;
        progressLabel.text = "\n\nStarting sync process:";
        syncProgress.value = 0;
        syncProgress.visible = true;
        progressCurrentItem.visible = true;

        // Pull student information
        progressLabel.text += "\nPulling student information...";
        r = mainWidget.canvas.pullStudentInfo();
        if (r === false) {
            progressLabel.text += "\n  ERROR pulling student info";
            progressLabel.text += "\n Unable to continue - Check network connection and try again.";
            return false;
        }
        syncProgress.value = .05;

        // Push assignments to the server
        progressLabel.text += "\nPushing Assignment Submissions...";
        syncProgress.value = 0.1;
        r = mainWidget.canvas.pushAssignments();
        if (r === false) { progressLabel.text += "\n ERROR pushing assingment submissions"; }

        // Pull classes
        progressLabel.text += "\nPulling courses from canvas...";
        r = mainWidget.canvas.pullCourses();
        if (r === false) { progressLabel.text += "\n  ERROR pulling course info"; }
        syncProgress.value = .2;

        progressLabel.text += "\nPulling modules for courses...";
        r = mainWidget.canvas.pullModules();
        if (r === false) { progressLabel.text += "\n  ERROR pulling module info"; }
        syncProgress.value = .25;

        progressLabel.text += "\nPulling items for all courses and modules...";
        r = mainWidget.canvas.pullModuleItems();
        if (r === false) { progressLabel.text += "\n  ERROR pulling item info"; }
        syncProgress.value = .27;

        // Pull pages for courses
        progressLabel.text += "\nPulling pages for courses...";
        r = mainWidget.canvas.pullCoursePages();
        if (r === false) { progressLabel.text += "\n  ERROR pulling pages"; }
        syncProgress.value = .3;

        // Pull assignments for courses
        progressLabel.text += "\nPulling assignments...";
        r = mainWidget.canvas.pullAssignments();
        if (r === false) { progressLabel.text += "\n ERROR pulling assignments"; }
        syncProgress.value = .35;

        // Pull inbox messages for user
        progressLabel.text += "\nPulling inbox messages for user...";
        r = mainWidget.canvas.pullMessages();
        if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }
        syncProgress.value = .4;

        // Pull sent messages for user
        progressLabel.text += "\nPulling sent messages for user...";
        r = mainWidget.canvas.pullMessages("sent");
        if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }
        syncProgress.value = .45;

        // Pull Announcements
        progressLabel.text += "\nPulling announcements...";
        r = mainWidget.canvas.pullAnnouncements();
        if (r === false) { progressLabel.text += "\n  ERROR pulling announcements"; }
        syncProgress.value = 0.48;

        progressLabel.text += "\nPulling Folder info for courses...";
        r = mainWidget.canvas.pullCourseFileFolders()
        if (r === false) { progressLabel.text += "\n  ERROR pulling folders info"; }
        syncProgress.value = .53;

        progressLabel.text += "\nPulling file info for courses...";
        r = mainWidget.canvas.pullCourseFilesInfo();
        if (r === false) { progressLabel.text += "\n  ERROR pulling files info"; }
        syncProgress.value = .56;

        // Pull SMC Documents
        progressLabel.text += "\nPulling SMC Documents...";
        r = mainWidget.canvas.pullSMCDocuments();
        if (r === false) { progressLabel.text += "\n  ERROR pulling SMC Documents"; }
        syncProgress.value = 0.6;

        // Don't do this unless its marked for pull
        progressLabel.text += "\nPulling file binaries...";
        r = mainWidget.canvas.pullCourseFilesBinaries();
        if (r === false) { progressLabel.text += "\n  ERROR pulling file binaries"; }
        syncProgress.value = 0.7;

        // Pull SMC Videos
        progressLabel.text += "\nPulling SMC Videos...";
        r = mainWidget.canvas.pullSMCVideos();
        if (r === false) { progressLabel.text += "\n  ERROR pulling SMC Videos"; }
        syncProgress.value = 0.8;

        // Fixup file download links
        progressLabel.text += "\nFixing file download links...";
        r = mainWidget.canvas.updateDownloadLinks();
        if (r === false) { progressLabel.text += "\n  ERROR fixing canvas links"; }
        syncProgress.value = 0.8;


        progressLabel.text += "\n\nDone!";
        syncProgress.visible = false;
        progressCurrentItem.visible = false;
        progressCurrentItem.text = "";

        // Mark that we have synced
        mainWidget.markAsSyncedWithCanvas();

    }



    header: Row {
        Button {
            id: syncButton
            text: "Sync with Canvas";
            onClicked: {
                syncPage.startSyncProcess();
            }
        }
        Button {
            id: closeButton
            text: "Close"
            onClicked: {
                syncDrawer.close();
            }
        }
    }

    contentData: Column {
        width: parent.width
        height: parent.height

        Row {
            width: parent.width
            height: 30
            ProgressBar {
                id: syncProgress
                visible: false;
                from: 0
                to: 1
                value: 0
            }
            Label {
                id: progressCurrentItem
                text: "Current Item"
                font.pixelSize: 12
            }
        }

        Label {
            id: progressLabel
            text: ""
            font.pixelSize: 18;
        }
    }
}
