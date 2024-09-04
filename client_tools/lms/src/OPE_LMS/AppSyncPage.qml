import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Universal 2.15
//import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.15
import QtQuick.Layouts 1.15

import QtWebView 1.1

import com.openprisoneducation.ope 1.0
import "App.js" as App

ColumnLayout {
    id: syncPage
    //contentHeight: 4
    //contentWidth: -3
    //anchors.fill: parent
    implicitWidth: parent.width;
    implicitHeight: parent.height;
    Layout.fillHeight: true;
    Layout.fillWidth: true;
    Layout.preferredHeight: parent.height;
    Layout.preferredWidth: parent.width;
    width: 800
    height: 600

    Connections {
        target: mainWidget.canvas;
        function onProgress(bytesRead, totalBytes, currentItem) {
            //console.log("dl progress called");
            progressCurrentItem.text = currentItem;

            if (totalBytes === 0) {
                syncProgress.value = 0

            } else {
                syncProgress.value = bytesRead / totalBytes;
            }
        }
    }

    function fixUpHTMLText(txt) {
        txt = txt.split("\n").join("<br />");

        txt = txt.replace(/ERROR -/g, "<span class='error'>ERROR</span> -");

        return txt;
    }

    function toggleRunning(is_running, txt) {
        closeButton.enabled = !is_running;
        syncButton.enabled = !is_running;
        syncingIndicator.running = is_running;

        // Set current item through C++ object which will propagate back
        // to qml via events
        mainWidget.canvas.setCurrentItem(progressLabel.initial_style + txt)
        // Also set here?
        progressCurrentItem.text = progressLabel.initial_style + txt;

    }

    function startSyncProcess()
    {
        var r;

        toggleRunning(true, "<span class='running'>Running Sync...</span>");

        // Reset with the style rules
        progressLabel.text = progressLabel.initial_style;

        progressLabel.text += "<h1>Starting sync process</h1>";
        syncProgress.value = 0;
        //syncProgress.visible = true;

        // Pull student information
        progressLabel.text += "<h2>Pulling student information...</h2>";
        r = mainWidget.canvas.pullStudentInfo();
        r = fixUpHTMLText(r);
        progressLabel.text += r;
        if (r.includes("ERROR")) {
            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
            return false;
        }
        syncProgress.value = .05;

        // Auto Accept pending invitations
        progressLabel.text += "<h2>Accepting course invitations...</h2>";
        r = mainWidget.canvas.autoAcceptCourses();
        r = fixUpHTMLText(r);
        progressLabel.text += r;
        if (r.includes("ERROR")) {
            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
            return false;
        }
        syncProgress.value = .075;

        // Push assignments to the server
        progressLabel.text += "<h2>Pushing Assignment Submissions...</h2>";
        syncProgress.value = 0.1;
        r = mainWidget.canvas.pushAssignments();
        r = fixUpHTMLText(r);
        progressLabel.text += r;
        if (r.includes("ERROR")) {
            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
            return false;
        }
        syncProgress.value = .15;

        //progressLabel.text += "\n\nDEBUG - QUIT EARLY!";
        //toggleRunning(false, "<span class='finished'>DEBUG QUIT - REMOVE FROM RELEASE CODE!!!</span>");
        //return;

        // Pull classes
        progressLabel.text += "<h2>Pulling courses from canvas...</h2>";
        r = mainWidget.canvas.pullCourses();
        r = fixUpHTMLText(r);
        progressLabel.text += r;
        if (r.includes("ERROR")) {
            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
            return false;
        }
        syncProgress.value = .2;

        progressLabel.text += "<h2>Pulling modules for courses...</h2>";
        r = mainWidget.canvas.pullModules();
        if (r === false) { progressLabel.text += "\n  ERROR pulling module info"; }
        syncProgress.value = .22;

        progressLabel.text += "<h2>Pulling items for all courses and modules...</h2>";
        r = mainWidget.canvas.pullModuleItems();
        if (r === false) { progressLabel.text += "\n  ERROR pulling item info"; }
        syncProgress.value = .24;

        progressLabel.text += "<h2>Pulling discussion topics for courses...</h2>";
        r = mainWidget.canvas.pullDiscussionTopics();
        r = fixUpHTMLText(r);
        progressLabel.text += r;
        if (r.includes("ERROR")) {
            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
            return false;
        }
        syncProgress.value = .26;

//        progressLabel.text += "<h2>Pulling quizzes for courses...</h2>";
//        r = mainWidget.canvas.pullQuizzes();
//        r = fixUpHTMLText(r);
//        progressLabel.text += r;
//        if (r.includes("ERROR")) {
//            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
//            return false;
//        }
//        syncProgress.value = .28;

//        progressLabel.text += "<h2>Pulling quiz questions for courses...</h2>";
//        r = mainWidget.canvas.pullQuizQuestions();
//        r = fixUpHTMLText(r);
//        progressLabel.text += r;
//        if (r.includes("ERROR")) {
//            toggleRunning(false, "<span class='error'>Fatal error - stopping sync!</span>");
//            return false;
//        }
//        syncProgress.value = .29;


        // Pull pages for courses
        progressLabel.text += "<h2>Pulling pages for courses...</h2>";
        r = mainWidget.canvas.pullCoursePages();
        if (r === false) { progressLabel.text += "\n  ERROR pulling pages"; }
        syncProgress.value = .3;

        // Pull assignments for courses
        progressLabel.text += "<h2>Pulling assignments...</h2>";
        r = mainWidget.canvas.pullAssignments();
        if (r === false) { progressLabel.text += "\n ERROR pulling assignments"; }
        syncProgress.value = .35;

        // Pull inbox messages for user
        progressLabel.text += "<h2>Pulling inbox messages for user...</h2>";
        r = mainWidget.canvas.pullMessages();
        if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }
        syncProgress.value = .4;

        // Pull sent messages for user
        progressLabel.text += "<h2>Pulling sent messages for user...</h2>";
        r = mainWidget.canvas.pullMessages("sent");
        if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }
        syncProgress.value = .45;

        // Pull Announcements
        progressLabel.text += "<h2>Pulling announcements...</h2>";
        r = mainWidget.canvas.pullAnnouncements();
        if (r === false) { progressLabel.text += "\n  ERROR pulling announcements"; }
        syncProgress.value = 0.48;

        progressLabel.text += "<h2>Pulling Folder info for courses...</h2>";
        r = mainWidget.canvas.pullCourseFileFolders()
        if (r === false) { progressLabel.text += "\n  ERROR pulling folders info"; }
        syncProgress.value = .53;

        progressLabel.text += "<h2>Pulling file info for courses...</h2>";
        r = mainWidget.canvas.pullCourseFilesInfo();
        if (r === false) { progressLabel.text += "\n  ERROR pulling files info"; }
        syncProgress.value = .56;

        // Pull SMC Documents
        progressLabel.text += "<h2>Pulling SMC Documents...</h2>";
        r = mainWidget.canvas.pullSMCDocuments();
        if (r === false) { progressLabel.text += "\n  ERROR pulling SMC Documents"; }
        syncProgress.value = 0.6;

        // Don't do this unless its marked for pull
        progressLabel.text += "<h2>Pulling file binaries...</h2>";
        r = mainWidget.canvas.pullCourseFilesBinaries();
        if (r === false) { progressLabel.text += "\n  ERROR pulling file binaries"; }
        syncProgress.value = 0.7;

        // Pull SMC Videos
        progressLabel.text += "<h2>Pulling SMC Videos...</h2>";
        r = mainWidget.canvas.pullSMCVideos();
        if (r === false) { progressLabel.text += "\n  ERROR pulling SMC Videos"; }
        syncProgress.value = 0.8;

        // Fixup file download links
        progressLabel.text += "<h2>Fixing file download links...</h2>";
        r = mainWidget.canvas.updateDownloadLinks();
        if (r === false) { progressLabel.text += "\n  ERROR fixing canvas links"; }
        syncProgress.value = 0.8;


        var finished_text = "<span class='finished'>Done With Sync!</span><br><br>";
        progressLabel.text += finished_text;

        syncProgress.value = 1.0;
        toggleRunning(false, finished_text);

        // Mark that we have synced
        mainWidget.markAsSyncedWithCanvas();

    }


    // Header Buttons
    RowLayout {
        Layout.fillHeight: false
        Layout.maximumHeight: 48
        Layout.alignment: Qt.AlignLeft | Qt.AlignTop
        Layout.fillWidth: true;
        Layout.preferredHeight: 48;
        Button {
            id: syncButton
            text: qsTr("Sync with Canvas");
            font.family: "Courier"
            Layout.fillHeight: false
            Layout.fillWidth: false
            Layout.preferredWidth: -1
            Layout.minimumWidth: 140
            //width: 40;
            property string text_color: App.text_color; // "#032569";
            property string text_down_color: App.text_color; //"#032569";
            spacing: 1
            display: AbstractButton.TextOnly
            onClicked: {
                syncPage.startSyncProcess();
            }

            contentItem:
                Text {
                    font.capitalization: Font.AllUppercase
                    color: parent.down ? parent.text_color : parent.text_down_color;
                    text: parent.text
                    font.bold: true
                    font.pointSize: 10
                    //lineHeight: 0.8
                    //font: parent.font
                    opacity: enabled ? 1.0 : 0.3
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
        }
        Button {
            id: closeButton
            text: "Close"
            Layout.fillHeight: false
            Layout.fillWidth: false

            property string text_color: App.text_color; // "#032569";
            property string text_down_color: App.text_color; // "#032569";

            display: AbstractButton.TextOnly
            onClicked: {
                // Clear text and Reset with the style rules
                progressLabel.text = progressLabel.initial_style;

                syncDrawer.close();
            }

            contentItem:
                Text {
                    font.capitalization: Font.AllUppercase
                    color: parent.down ? parent.text_color : parent.text_down_color;
                    text: parent.text
                    font.bold: true
                    font.pointSize: 10
                    //lineHeight: 0.8
                    //font: parent.font
                    opacity: enabled ? 1.0 : 0.3
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
        }
        Label {
            id: header_spacer
            text: "";
            Layout.fillWidth: true;
            Layout.fillHeight: false;
            Layout.minimumHeight: 1

        }

        BusyIndicator {
            id: syncingIndicator
            hoverEnabled: false
            running: false
            Layout.minimumHeight: 30
            Layout.minimumWidth: 30
            transformOrigin: Item.Right
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter


        }
    }

    // Page Contents
    ColumnLayout {
        Layout.alignment: Qt.AlignLeft | Qt.AlignTop
        //width: parent.width
        //height: parent.height
       spacing: 5
       Layout.fillHeight: true
       Layout.fillWidth: true;

       ColumnLayout {
           //width: parent.width
           height: 40
           Layout.fillHeight: false
           Layout.fillWidth: true;


           Label {
               Layout.fillWidth: true;
               //Layout.fillHeight: true;
               Layout.preferredHeight: -1
               id: progressCurrentItem
               //text: "<style>*, span, div, html, body { color: 'red'; }</style>testing text<p> P TEXT</p>"
               antialiasing: false
               Layout.minimumWidth: 30
               Layout.alignment: Qt.AlignLeft | Qt.AlignTop
               Layout.fillHeight: false
               font.pixelSize: 12
               textFormat: "RichText";
               color: App.text_color;
           }

           ProgressBar {
               id: syncProgress
               Layout.alignment: Qt.AlignLeft | Qt.AlignTop
               Layout.fillHeight: false
               visible: true;
               from: 0
               to: 1
               value: 0
               Layout.fillWidth: true
               Layout.preferredHeight: 5
               Layout.maximumHeight: 5

           }
       }

       /*
       Label {
           id: progressLabel
           text: ""
           Layout.alignment: Qt.AlignLeft | Qt.AlignTop
           //width: parent.width;
           wrapMode: Text.Wrap;
           font.pixelSize: 18;
           Layout.fillHeight: true
           Layout.fillWidth: true

       }*/

       ScrollView {
           //contentWidth: 386
           //ScrollBar.horizontal.policy: ScrollBar.AlwaysOff;
           //ScrollBar.vertical.policy: ScrollBar.AlwaysOn;
           clip: true;
           Layout.fillHeight: true;
           Layout.fillWidth: true;
           wheelEnabled: true;
           id: progressLabelScrollView

           contentChildren:
               Label {
                   id: progressLabel

                   onTextChanged: {
                       // Make the scroll view slide down
                       //console.log("text changed!!!!");
                       //progressLabelScrollView.ScrollBar.vertical.position = 1.0;
                       progressLabelScrollView.ScrollBar.vertical.increase();
                   }

// Possible font sizes: xx-small, x-small, small, medium, large, x-large, xx-large, xxx-large
// larger, smaller, percentage?
                   property string initial_style: "
<style>
 h1 { color: '#032569'; font-size: x-large; }
 h2 { color: '#032569'; font-size: medium; }
 .error {color: 'red'; font-size: 24px; }
 .finished { color: '#1f8e44'; font-size: 24px; }
 .running { color: '#6b8574'; font-size: 24px; }
 .failed {color: 'red'; }
 .accepted { color: '#1f8e44'; }
 body { color: '#3e4c5f'; }
</style>

";
                   //text: initial_style;
                   Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                   //width: parent.width;
                   wrapMode: Text.Wrap;
                   font.pixelSize: 16;
                   Layout.fillHeight: true
                   Layout.fillWidth: true
                   textFormat: "RichText";
                   color: App.text_color; //"#3e4c5f"
                   padding: 5;
                   width: progressLabelScrollView.width;
                   height: progressLabelScrollView.height;

               }

       }


   }

}
