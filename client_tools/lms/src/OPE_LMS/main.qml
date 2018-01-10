import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.2
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4

import "App.js" as App

ApplicationWindow {
    visible: true
    id: window
    objectName: "window"
    width: 900
    height: 600
    title: qsTr("OPE - Learning Resource System")


    Component.onCompleted: {
        // if first run, open up the first run drawer
        if (mainWidget.isAppCredentialed() === false) {
            syncDrawer.open();
            //firstRunDrawer.open();
        }

        // Make sure we set the current course
        App.current_course = App.getFieldValue(selectedCourse.model, selectedCourse.currentIndex, "id");
        console.log(App.current_course);
        pageLoader.item.refreshPage();
    }

    Connections {
//        target: mainWidget
//        onShowCanvasLogin:
//        {
//            //console.log("Change url: " + url);
//            loginWebView.url = url;
//        }

        target: pageLoader.item
        onLoadPage: {
            console.log("Load Page Called: " + page_url);
            App.current_page_url = page_url;
            pageLoader.setSource("CanvasPage.qml");
        }
    }

    header: ToolBar
    {
        RowLayout {
            anchors.fill: parent;
//            ToolButton {
//                text: qsTr("Login")
//                onClicked: loginDrawer.open();
//            }
            ToolButton {
                text: qsTr("Sync With Canvas")
                onClicked: {
                    if(syncDrawer.position < 0.1) {
                        syncDrawer.open();
                    }
                }
            }

            ToolButton {
                text: qsTr("Resources");
                visible: false
                onClicked: {
                    if (resourcesDrawer.position < 0.1) {
                        resourcesDrawer.open();
                    }
                }
            }
        }

    }

    Drawer {
        id: firstRunDrawer
        y: 0
        width: window.width * 1.0;
        height: window.height;
        edge: Qt.RightEdge;
        dragMargin: 0;
        closePolicy: Popup.NoAutoClose;

        ColumnLayout {
            Label {
                text: "Student Setup";
                font.pixelSize: 24;
                font.bold: true;
                color: "darkblue"

            }
        }
    }

    Drawer
    {
        id: loginDrawer
        y: 0; //header.height
        width: window.width * 1.0
        height: window.height; //window.height - header.height
        edge: Qt.LeftEdge
        dragMargin: 0

        ColumnLayout
        {
            Label {
                text: "Login To Canvas"
                font.bold: true;
                font.pixelSize: 24;
                color: "darkblue";
            }
            GridLayout
            {
                columns: 2

                Label { text: "User Name:"; }
                TextField {
                    id: user_name;
                    placeholderText: qsTr("Enter User Name")
                }

                Label { text: "Password:"; }
                TextField {
                    id: password
                    placeholderText: qsTr("Enter Password")
                    passwordCharacter: "*"
                    echoMode: TextInput.Password
                }

                Button {
                    text: "Login"
                    onClicked: {
                        //var ret = database.auth_student(user_name.text, password.text);
                        var ret = mainWidget.canvasAuthenticateUser(user_name.text, password.text);
                        if (ret === true) {
                            // Login succeeded
                            loginMessage.text = "Found local account - welcome";
                        } else {
                            // Login failed
                            loginMessage.text = "Invalid username or password!";
                        }
                    }
                }
                Button {
                    text: "Cancel"
                    onClicked: loginDrawer.close();
                }
            }
            Label {
                id: loginMessage
                text: ""
                color: "#ff0000"

            }
            Label {
                text: loginWebView.url
            }

            Label {
                text: loginWebView.title
            }

            Rectangle
            {
                color: "darkblue"
                width: 600
                height: 300


                WebEngineView {
                   anchors.fill: parent
                   id: loginWebView
                   objectName: "loginWebView"
                   width: 800
                   height: 300
                   //url: 'https://canvas.correctionsed.com/login/oauth2/auth?client_id=10000000000004&redirect_uri=http://localhost:1337/cb&response_type=code&scope&state=GlzDhlij'
                   //url: "https://canvas.correctionsed.com/login";

                   //Component.onCompleted: { loginWebView.loadHtml("HELLO"); }
                   Component.onCompleted: {
                       //mainWidget.setupLoginWebView(loginWebView);
                   }

                   onCertificateError:
                   {
                       // Allow test certs
                       //console.log("Ignore ssl error?");
                       error.ignoreCertificateError();
                       return true;
                   }

                   onLoadingChanged: {
                       console.log("Loading changed..." + loadRequest.url);
                       console.log("Status: " + loadRequest.status + " -- Start: " +
                                   WebEngineView.LoadStartedStatus + ", Stopped: " + WebEngineView.LoadStoppedStatus +
                                   ", Success: " + WebEngineView.LoadSucceededStatus + ", Failed: " + WebEngineView.LoadFailedStatus);
                       if (loadRequest.errorString)
                           console.error("Error String: " + loadRequest.errorString);
                       console.log(loginWebView.Page);
                       if (loadRequest.status === WebEngineLoadRequest.LoadSuccessStatus) {
                           if (loadRequest.url.indexOf("localhost:1337/cb?code=") !== -1) {
                               // Confirm?
                               console.log("Confirm login");
                           }
                       }
                   }

               }
            }


        }

    }

    Drawer
    {
        id: resourcesDrawer
        y: header.height
        width: window.width * 0.4
        height: window.height - header.height
        edge: Qt.RightEdge
        dragMargin: 0

        ColumnLayout {
            Label {
                id: resources_title
                text: "Resources"
            }

            ListView {
                width: parent.width
                height: parent.height - resources_title.height
                model: resources_model

                highlight: Rectangle { color: "lightsteelblue"; radius: 2; }

                delegate: Text {
                    text: resource_name

                }
            }
        }

    }


    Drawer {
        id: syncDrawer
        y: header.height
        width: window.width // * 0.99
        height: window.height - header.height
        edge: Qt.RightEdge
        dragMargin: 0


        Page {
            id: syncPage
            anchors.fill: parent

            Connections {
                target: mainWidget.canvas;
                onDlProgress: {
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

                // Pull student information
                progressLabel.text += "\nPulling student information...";
                r = mainWidget.canvas.pullStudentInfo();
                if (r === false) { progressLabel.text += "\n  ERROR pulling student info"; }
                syncProgress.value = .1;

                // Pull classes
                progressLabel.text += "\nPulling courses from canvas...";
                r = mainWidget.canvas.pullCourses();
                if (r === false) { progressLabel.text += "\n  ERROR pulling course info"; }
                syncProgress.value = .2;

                progressLabel.text += "\nPulling modules for courses...";
                r = mainWidget.canvas.pullModules();
                if (r === false) { progressLabel.text += "\n  ERROR pulling module info"; }
                syncProgress.value = .3;

                progressLabel.text += "\nPulling items for all courses and modules...";
                r = mainWidget.canvas.pullModuleItems();
                if (r === false) { progressLabel.text += "\n  ERROR pulling item info"; }
                syncProgress.value = .4;

                progressLabel.text += "\nPulling file info for courses...";
                r = mainWidget.canvas.pullCourseFilesInfo();
                if (r === false) { progressLabel.text += "\n  ERROR pulling files info"; }
                syncProgress.value = .5;

                // Pull pages for courses
                progressLabel.text += "\nPulling pages for courses...";
                r = mainWidget.canvas.pullCoursePages();
                if (r === false) { progressLabel.text += "\n  ERROR pulling pages"; }
                syncProgress.value = .6;

                // Pull assignments for courses
                progressLabel.text += "\nPulling assignments...";
                r = mainWidget.canvas.pullAssignments();
                if (r === false) { progressLabel.text += "\n ERROR pulling assignments"; }
                syncProgress.value = .65;

                // Pull inbox messages for user
                progressLabel.text += "\nPulling inbox messages for user...";
                r = mainWidget.canvas.pullMessages();
                if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }
                syncProgress.value = .7;

                // Pull sent messages for user
                progressLabel.text += "\nPulling sent messages for user...";
                r = mainWidget.canvas.pullMessages("sent");
                if (r === false) { progressLabel.text += "\n  ERROR pulling messages"; }
                syncProgress.value = .8;

                // Don't do this unless its marked for pull
                progressLabel.text += "\nPulling file binaries...";
                r = mainWidget.canvas.pullCourseFilesBinaries();
                if (r === false) { progressLabel.text += "\n  ERROR pulling file binaries"; }
                syncProgress.value = 1.0;

                progressLabel.text += "\n\nDone!";
                syncProgress.visible = false;

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
    }

    Drawer
    {
        id: syncDrawerOld
        y: header.height
        width: window.width * 0.6
        height: window.height - header.height
        edge: Qt.RightEdge
        dragMargin: 0

        ColumnLayout
        {
            Label { text: "Sync..."; }

            WebEngineView {
               anchors.fill: parent
               id: syncWebView
               objectName: "syncWebView"
               width: 800
               height: 300
               //url: 'https://canvas.correctionsed.com/login/oauth2/auth?client_id=10000000000004&redirect_uri=http://localhost:1337/cb&response_type=code&scope&state=GlzDhlij'
               //url: "https://canvas.correctionsed.com/login";

               onCertificateError:
               {
                   // Allow test certs
                   error.ignoreCertificateError();
                   return true;
               }

               onLoadingChanged: {
                   console.log("Loading changed..." + loadRequest.url);
                   console.log("Status: " + loadRequest.status + " -- Start: " +
                               WebEngineView.LoadStartedStatus + ", Stopped: " + WebEngineView.LoadStoppedStatus +
                               ", Success: " + WebEngineView.LoadSucceededStatus + ", Failed: " + WebEngineView.LoadFailedStatus);
                   if (loadRequest.errorString)
                       console.error("Error String: " + loadRequest.errorString);
                   if (loadRequest.status === WebEngineLoadRequest.LoadSuccessStatus) {
                       if (loadRequest.url.indexOf("localhost:1337/cb?code=") !== -1) {
                           // Confirm?
                           console.log("Confirm login");
                       }
                   }
               }
            }
        }

    }


    Page {
        id: mainPage
        anchors.fill: parent

        SplitView {
            anchors.fill: parent
            orientation: Qt.Horizontal
            resizing: true

            Pane {
                width: 250
                height: parent.height

                ColumnLayout {
                    anchors.right: parent.right
                    anchors.left: parent.left
                    height: parent.height

                    ComboBox {
                        Layout.fillWidth: true
                        id: selectedCourse
                        model: courses_model
                        textRole: "name"
                        onActivated: {
                            App.current_course = App.getFieldValue(this.model, index, "id");
                            console.log(App.current_course);
                            pageLoader.item.refreshPage();
                        }

                    }

                    Pane {
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        leftPadding: 0
                        rightPadding: 0

                        /*
                        Rectangle {
                            color: "red"
                            width: parent.width
                            height: parent.height
                        }*/


                        ListView {
                            width: parent.width
                            height: parent.height
                            id: courseTabs
                            interactive: false
                            focus: true
                            spacing: 4
                            highlightFollowsCurrentItem: true

                            highlight: Rectangle {
                                width: parent.width
                                height: 30
                                color: "steelblue"
                                radius: 3
                            }

                            delegate: Component {
                                Rectangle {
                                    id: item
                                    Layout.fillWidth: true
                                    width: parent.width
                                    height: 30
                                    implicitHeight: height
                                    color: "lightgrey"
                                    radius: 3
                                    opacity: 0.5
                                    property int indexOfThisDelegate: index

                                    Row {
                                        Text {
                                            height: 30
                                            verticalAlignment: Text.AlignVCenter
                                            text: name
                                            font.bold: true
                                            font.pixelSize: 18
                                        }
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onEntered: { parent.color="lightsteelblue" }
                                        onExited: { parent.color="lightgrey" }
                                        onClicked: {
                                            // Set the current tab
                                            courseTabs.currentIndex = indexOfThisDelegate
                                            // Load the page
                                            pageLoader.setSource(name + ".qml");

                                        }
                                    }
                                }
                            }

                            model: ListModel {
                                id: courseTabsModel
                                ListElement { name: "Home"; order: 0; enabled: true }
                                ListElement { name: "Modules"; order: 1; enabled: true }
                                ListElement { name: "Pages"; order: 2; enabled: true }
                                //ListElement { name: "Assignments"; order: 3; enabled: true }
                                //ListElement { name: "Quizzes"; order: 4; enabled: true }
                                //ListElement { name: "Inbox"; order: 5; enabled: true }
                                //ListElement { name: "Calendar"; order: 6; enabled: false }
                                ListElement { name: "Announcements"; order: 7; enabled: false }
                                //ListElement { name: "Discussions"; order: 8; enabled: false }
                                //ListElement { name: "Grades"; order: 9; enabled: false }
                                ListElement { name: "Files"; order: 10; enabled: true }
                                //ListElement { name: "Syllabus"; order: 11; enabled: true }

                            }
                        }
                    }


                }
            }

            Page {
                Loader {
                    id: pageLoader
                    anchors.fill: parent
                    source: "Home.qml"
                }
            }



/*
            Page {

                SwipeView {
                    id: courseView
                    anchors.fill: parent
                    currentIndex: courseTabs.currentIndex
                    interactive: false




                }

            } */

        }
    }

    //footer:


}
