import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Universal
////import QtQuick.Controls.Styles
import QtQuick.Controls.Imagine
import QtQuick.Layouts

import QtWebView 1.1


import QtWebChannel 1.0
import QtWebSockets 1.1
import cm.WebSocketTransport 1.0

import com.openprisoneducation.ope 1.0
import "App.js" as App

ApplicationWindow {
    visible: true;
    visibility: "Windowed"; // "FullScreen"
    flags: (Qt.Window) ; // Qt.WindowStaysOnTopHint
    id: main_window
    objectName: "main_window"


    width: 900
    height: 600
    property alias rectangle1: rectangle1

    property string current_course_id: "";
    property string current_page_url: "";
    property string current_assignment_id: "";
    property string current_module_item_id: "";
    property string current_quiz_id: "";
    property string current_discussion_id: "";


    // === SETUP WEB CHANNEL - allow webview pages to interact w LMS ===
    property QtObject lmsObject: QtObject {
        // This object is exposed to the webviews so that they can call
        // back into the app when needed; currently used for:
        // - override link clicks for local files
        id: lmsObject
        WebChannel.id: "LMS"
        // property string somProperty: "value";
        signal someSignal(string message);

        function openDesktopLink(link_url) {
            // Open the link using the desktop app
            console.log("lmsObject===> Opening Link: " + link_url);
            var r = mainWidget.desktopLaunch(link_url);
            return r;
        }

        function log(msg) {
            console.log("lmsObject===> WVLog: " + msg);
            return 0;
        }
    }

    WebSocketTransport {
        id: wsTransport
    }
    WebSocketServer {
        id: wsServer
        accept: true;
        name: "OPE_WS_Server"
        //host: "localhost"
        port: 65524
        listen: true

        onClientConnected: {
            console.log("WCClient Connected: " + webSocket.status + " - " + webSocket.errorString);

            if(webSocket.status === WebSocket.Open) {
                console.log("WCClient - Is Open");
                webChannel.connectTo(wsTransport);
                webSocket.onTextMessageReceived.connect(wsTransport.textMessageReceive);
                wsTransport.onMessageChanged.connect(webSocket.sendTextMessage);
            } else {
                console.log("Unknonw WCClient error " + webSocket.errorString);
            }
        }
        onErrorStringChanged: {
            console.log("WS Server Error: %1".arg(errorString));
        }

        Component.onCompleted: {
            console.log("WS Server Running: " + wsServer.url);
        }
    }
    WebChannel {
        id: webChannel
        registeredObjects: [lmsObject]
    }
    // === END SETUP WEB CHANNEL ===

    title: qsTr("OPE - Offline LMS");


    function showFeedView() {
        console.log("showFeedView called...");
    }

    function showModulesView() {
        console.log("showModulesView called...");
        appStack.replace(appModulesListView);
    }

    function showAssignmentsView() {
        console.log("showAssignmentsView called...");
        appStack.replace(appAssignmentsListView);
    }

    function showSyllabusViewe() {
        console.log("showSyllabusView called...");
    }

    function showWikiPageView() {
        console.log("showWikiPageView called...");
        appStack.replace(appWikiPageView);
    }



    Component.onCompleted: {
        //console.log("need_sync " + need_sync);
        //if (need_sync === true || mainWidget.isAppCredentialed() === false ) {
        //    syncDrawer.open();
        //}

        // Find current course
        //var m = courses_model;
        //courses_model.modifyFilter("is_active='true'");
        //courses_model.sortOn('name');
        //App.current_course = App.getFieldValue(selectedCourse.model, selectedCourse.currentIndex, "id");
        //console.log(App.current_course);
        //pageLoader.item.refreshPage();

    }





    Page {
        id: appPage
        anchors.fill: parent

        header: ToolBar {
            //opacity: 0.5
            implicitHeight: 48;

            RowLayout {
                anchors.fill: parent;


                ToolButton {
                    id: tbSyncWithCanvas
                    text: "Sync With Canvas";
                    Layout.minimumWidth: 48
                    Layout.preferredWidth: 48
                    Layout.preferredHeight: parent.height
                    Layout.maximumWidth: 48

                    contentItem: Image {
                        source: "qrc:/images/sync.png"
                        width: tbSyncWithCanvas.width;
                        height: tbSyncWithCanvas.height;
                    }

                    onClicked: {
                        if (syncDrawer.position < 0.1) {
                            syncDrawer.open();
                        }
                    }
                }



                Rectangle {
                    width: 80
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    Layout.preferredWidth: width
                    Layout.preferredHeight: parent.height
                    Layout.minimumWidth: width


                    AppCourseSelector {
                        id: appCourseSelector
                        anchors.fill: parent
                        global: main_window;
                        current_course_id: main_window.current_course_id;

                        onChanged:  {
                            console.log("Course Changed " + current_course_id);

                            // Have sidebar select home tab, should fire event
                            // which will reload the main page
                            appSideBar.selectMenuTab("Home");

                            // Reload home page for this course
                            //appStack.replace(appHomePageView);
                        }

                    }
                }

            }
        }


        RowLayout {
            anchors.fill: parent
            spacing: 3

            Rectangle {
                width: 250
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.preferredWidth: width
                Layout.preferredHeight: 200
                Layout.minimumWidth: width
                Layout.maximumWidth: width
                //color: "#eeeeee"


                ColumnLayout {
                    //Layout.fillHeight: true
                    anchors.fill: parent
                    spacing: 3

                    Item {
                        id: rectangle
                        Layout.preferredHeight: 1
                        Layout.preferredWidth: 80
                        Layout.fillWidth: true
                        //color: "#aaaaaa"
                        Layout.margins: 3

                    }


                    Item {
                        id: rectangle1
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.minimumHeight: 60
                        Layout.minimumWidth: 80
                        Layout.margins: 3
                        //color: "#aaaaaa"

                        AppSideBar {
                            id: appSideBar
                            anchors.fill: parent

                            onClicked: function(tab_name){
                                console.log("Sidebar Clicked: " + tab_name);

                                switch(tab_name) {

                                case "Assignments":
                                    appStack.replace(appAssignmentsListView);
                                    break;
                                case "Modules":
                                    appStack.replace(appModulesListView);
                                    break;
                                case "Pages":
                                    appStack.replace(appPagesView);
                                    break;
                                case "Files":
                                    appStack.replace(appFilesView);
                                    break;
                                case "Announcements":
                                    appStack.replace(appAnnouncementsView);
                                    break;
                                case "Inbox":
                                    appStack.replace(appInboxView);
                                    break;
                                case "Quizzes":
                                    appStack.replace(appQuizzesView);
                                    break;
                                case "Discussions":
                                    appStack.replace(appDiscussionsView);
                                    break;
                                default:
                                    appStack.replace(appHomePageView);
                                    break;
                                }

                            }

                        }
                    }

                }


            }


            Rectangle {
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.minimumWidth: 120
                Layout.minimumHeight: 120
                Layout.preferredHeight: 200
                Layout.preferredWidth: 200
                //color: "#0000ff"
                clip: true

                StackView {
                    id: appStack
                    anchors.fill: parent

                    initialItem: appHomePageView
                }
            }
        }

    }











    Component {

        id: appHomePageView
        AppHomePage {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_page_url: main_window.current_page_url;
            current_assignment_id: main_window.current_assignment_id;
        }
    }

    Component {
        id: appWikiPageView
        AppWikiPage {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_page_url: main_window.current_page_url;
        }
    }

    Component {
        id: appPagesView
        AppPages {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_page_url: main_window.current_page_url;
            onPageClicked: {
                console.log("Page Clicked: " + page_url);
                appStack.replace(appWikiPageView);
            }
        }
    }

    Component {
        id: appFilesView
        AppFiles {
            global: main_window;
            current_course_id: main_window.current_course_id
        }
    }

    Component {
        id: appAssignmentsListView
        AppAssignments {
            global: main_window;
            current_assignent_id: main_window.current_assignment_id;
            current_course_id: main_window.current_course_id;
            onAssignmentClicked: {
                console.log("Assignment Clicked: " + assignment_id);
                appStack.replace(appAssignmentPage);
            }
        }
    }


    Component {
        id: appAssignmentPage
        AppAssignmentPage {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_assignment_id: main_window.current_assignment_id;
        }
    }


    Component {
        id: appModulesListView
        AppModules {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_page_url: main_window.current_page_url;
            current_assignment_id: main_window.current_assignment_id;

            onModulePageClicked: {
                // Switch to page view
                console.log("Module page clicked: " + page_url)
                appStack.replace(appWikiPageView);
            }
            onModuleAssignmentClicked: {
                // Switch to assignment View
                console.log("Module Assignment Clicked: " + assignment_id);
                appStack.replace(appAssignmentPage);
            }
        }
    }

    Component {
        id: appAnnouncementsView
        AppAnnouncements {
            global: main_window;
            current_course_id: main_window.current_course_id;
        }
    }

    Component {
        id: appInboxView
        AppInbox {
            global: main_window;
            current_course_id: main_window.current_course_id;
        }
    }


    Component {
        id: appQuizzesView
        AppQuizzes {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_quiz_id: main_window.current_quiz_id;
            onQuizClicked: {
                console.log("Quiz Clicked: " + quiz_id);
                appStack.replace(appQuizzesView);
            }
        }
    }

    Component {
        id: appDiscussionsView
        AppDiscussions {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_discussion_id: main_window.current_discussion_id;
            onDiscussionClicked: {
                console.log("Discussion Clicked: " + discussion_id);
                appStack.replace(appDiscussionsView);
            }
        }
    }



    Drawer {
        id: syncDrawer
        y: appPage.y
        width: appPage.width // * 0.99
        height: appPage.height
        edge: Qt.RightEdge
        dragMargin: 0
        interactive: false;
        position: 0.0;

        Rectangle {
            width: syncDrawer.width;
            height: syncDrawer.height;
            //implicitWidth: parent.width;
            //implicitHeight: parent.height;
            Layout.preferredHeight: syncDrawer.height;
            Layout.preferredWidth: syncDrawer.width;
            Layout.fillWidth: true;
            Layout.fillHeight: true;
            color: App.page_bg_color;

            AppSyncPage {
                //anchors.fill: parent;
                width: syncDrawer.width;
                height: syncDrawer.height;
                //implicitWidth: parent.width;
                //implicitHeight: parent.height;
                Layout.preferredHeight: syncDrawer.height;
                Layout.preferredWidth: syncDrawer.width;
                Layout.fillWidth: true;
                Layout.fillHeight: true;

            }
        }



    }



}
