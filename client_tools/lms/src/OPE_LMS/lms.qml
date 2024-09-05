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

//    Accessible.name: "Open Prison Education - Main Window";
//    Accessible.description: "Offline Canvas Learning Management System";
//    Accessible.role: Accessible.Window;


    width: 1100
    height: 800
    property alias rectangle1: appSideBarParent

    property string current_course_id: "";
    property string current_course_name: "";
    property string current_course_code: "";
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
        objectName: "appPage"
        anchors.fill: parent
        property int gnav_width: global_nav_sidebar.width;

        Accessible.name: "Open Prison Education - Main Window";
        Accessible.description: "Offline Canvas Learning Management System";
        Accessible.role: Accessible.PageTab;


        header: ToolBar {
            //opacity: 0.5
            implicitHeight: 0; //48;
            height:0;
            background: Rectangle {
                color: App.global_nav_background;
            }

            RowLayout {
                anchors.fill: parent;

                //                ToolButton {
                //                    id: tbSyncWithCanvas
                //                    text: "Sync With Canvas";
                //                    Layout.minimumWidth: 48
                //                    Layout.preferredWidth: 48
                //                    Layout.preferredHeight: parent.height
                //                    Layout.maximumWidth: 48

                //                    background: Rectangle {
                //                        color: App.global_nav_background;
                //                    }

                //                    contentItem: Image {
                //                        source: "qrc:/images/sync.png"
                //                        width: tbSyncWithCanvas.width;
                //                        height: tbSyncWithCanvas.height;
                //                    }

                //                    onClicked: {
                //                        if (syncDrawer.position < 0.1) {
                //                            syncDrawer.open();
                //                        }
                //                    }
                //                }



                Rectangle {
                    width: 80
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    Layout.preferredWidth: width
                    Layout.preferredHeight: parent.height
                    Layout.minimumWidth: width

                    AppCourseSelector {
                        id: appCourseSelector;
                        anchors.fill: parent;
                        global: main_window;
                        current_course_id: main_window.current_course_id;
                        visible: false;

                        onChanged:  {
                            return; // Don't use dropdown course selector anymore
                            //console.log("Course Changed " + current_course_id);

                            // Have sidebar select home tab, should fire event
                            // which will reload the main page
                            //appSideBar.selectMenuTab("Home");

                            // Reload home page for this course
                            //appStack.replace(appHomePageView);
                        }

                    }
                }

            }
        }


        RowLayout {
            anchors.fill: parent
            spacing: 0

            Rectangle {
                id: global_nav_sidebar_maximize;
                property int open_width: 24;
                width: 0;
                Layout.fillHeight: true;
                Layout.preferredWidth: global_nav_sidebar_maximize.open_width;
                Layout.preferredHeight: 200;
                Layout.minimumWidth: width;
                Layout.maximumWidth: width;

                color: App.global_nav_background;

                states: [
                    State {
                        name: "open";
                        PropertyChanges{ global_nav_sidebar_maximize.width: global_nav_sidebar_maximize.open_width; }
                    },
                    State {
                        name: "closed";
                        PropertyChanges { global_nav_sidebar_maximize.width: 0; }
                    }
                ]

                transitions: Transition {
                    NumberAnimation {
                        properties: "width";
                        duration: 450;
                        easing.type: Easing.InOutQuad;
                    }
                }
                ColumnLayout {
                    anchors.fill: parent;
                    spacing: 0;
                    width: parent.width;
                    Layout.fillHeight: true;
                    Layout.fillWidth: true;
                    Layout.preferredWidth: width;
                    Layout.preferredHeight: 200;

                    Button {
                        id: gnav_maximize_button
                        width: parent.width;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignCenter;
                        //color: App.global_nav_background;

                        property string button_text: "Maximize Navigation Menu"

                        Accessible.name: "Maximize"
                        Accessible.description: "Expand global navigation";
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if(hovered) {
                                gnav_maximize_button.focus = true;
                                gnav_maximize_button.forceActiveFocus();
                                gnav_maximize_button.activeFocusChanged(true);
                                gnav_maximize_tooltip.show(gnav_maximize_button.button_text);
                            } else {
                                gnav_maximize_button.focus = false;
                                gnav_maximize_button.focusChanged(false);
                                gnav_maximize_tooltip.hide();
                            }
                        }

                        onClicked: {
                            global_nav_sidebar.state = "open";
                            global_nav_sidebar_maximize.state = "closed";

                        }

                        contentItem: Item {
                            Image {
                                source: "qrc:/images/global_nav_maximize.png";
                                width: parent.width;
                                //height: 74;
                                fillMode: Image.PreserveAspectFit
                                anchors.horizontalCenter: parent.horizontalCenter;
                                anchors.verticalCenter: parent.verticalCenter;
                            }

                            ToolTip {
                                id: gnav_maximize_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_maximize_tooltip.text
                                    font: gnav_maximize_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }
                }
            }

            Rectangle {
                id: global_nav_sidebar;
                width: 84;
                Layout.fillHeight: true;
                Layout.preferredWidth: 84;
                Layout.preferredHeight: 200;
                Layout.minimumWidth: width;
                Layout.maximumWidth: width;

                color: App.global_nav_background;

                states: [
                    State {
                        name: "open";
                        PropertyChanges{ global_nav_sidebar.width: 84; }
                    },
                    State {
                        name: "closed";
                        PropertyChanges { global_nav_sidebar.width: 0; }
                    }
                ]

                transitions: Transition {
                    NumberAnimation {
                        properties: "width";
                        duration: 450;
                        easing.type: Easing.InOutQuad;
                    }
                }

                ColumnLayout {
                    anchors.fill: parent;
                    spacing: 0;
                    width: 84;
                    Layout.fillHeight: true;
                    Layout.fillWidth: true;
                    Layout.preferredWidth: 84;
                    Layout.preferredHeight: 200;

                    Button {
                        id: gnav_home_page_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "Home Screen"

                        Accessible.name: button_text;
                        Accessible.description: "Home Screen"
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if(hovered) {
                                gnav_home_page_button.focus = true;
                                gnav_home_page_button.forceActiveFocus();
                                gnav_home_page_button.focusChanged(true);
                                gnav_home_tooltip.show(button_text);
                            } else {
                                gnav_home_page_button.focus = false;
                                gnav_home_page_button.focusChanged(false);
                                gnav_home_tooltip.hide();
                            }
                        }

                        onClicked: {
                            appBreadCrumb.close();
                            appStack.replace(appDashboardView);
                        }

                        contentItem: Item {
                            Image {
                                source: "qrc:/images/global_nav_canvas.png";
                                width: 74;
                                height: 74;
                                fillMode: Image.PreserveAspectFit
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            ToolTip {
                                id: gnav_home_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_home_tooltip.text
                                    font: gnav_home_tooltip.font
                                    color: "white";
                                }
                            }

                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }


                    Button {
                        id: gnav_account_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "Account Information"

                        Accessible.name: button_text
                        Accessible.description: "Accounnt Information"
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if (hovered) {
                                gnav_account_button.focus = true;
                                gnav_account_button.forceActiveFocus();
                                gnav_account_button.focusChanged(true);
                                gnav_account_tooltip.show(button_text);
                            } else {
                                gnav_account_button.focus = false;
                                gnav_account_button.focusChanged(false);
                                gnav_account_tooltip.hide();
                            }
                        }

                        onClicked: {

                        }

                        contentItem: Item {
                            Image {
                                id: gnav_account_image
                                source: "qrc:/images/global_nav_avatar-50.png";
                                width: 64;
                                height: 64;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_account_text;
                                z: gnav_account_image.z + 1;
                                text: qsTr("Account");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_account_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_account_tooltip.text
                                    font: gnav_account_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }

                    Button {
                        id: gnav_dashboard_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "View your dashboard"

                        Accessible.name: "Dashboard"
                        Accessible.description: "View your dashboard";
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if (hovered) {
                                gnav_dashboard_button.focus = true;
                                gnav_dashboard_button.forceActiveFocus();
                                gnav_dashboard_button.focusChanged(true);
                                gnav_dashboard_tooltip.show(button_text);
                            } else {
                                gnav_dashboard_button.focus = false;
                                gnav_dashboard_button.focusChanged(false);
                                gnav_dashboard_tooltip.hide();
                            }
                        }

                        onClicked: {
                            appBreadCrumb.close();
                            appStack.replace(appDashboardView);
                        }

                        contentItem: Item {
                            Image {
                                id: gnav_dashboard_image
                                source: "qrc:/images/global_nav_dashboard.png";
                                width: 54;
                                height: 54;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_dashboard_text
                                z: gnav_dashboard_image.z + 1;
                                text: qsTr("Dashboard");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_dashboard_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_dashboard_tooltip.text
                                    font: gnav_dashboard_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }

                    Button {
                        id: gnav_courses_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "Courses you are enrolled in"

                        Accessible.name: "Courses";
                        Accessible.description: button_text;
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if(hovered) {
                                gnav_courses_button.focus = true;
                                gnav_courses_button.forceActiveFocus();
                                gnav_courses_button.focusChanged(true);
                                gnav_courses_tooltip.show(button_text);
                            } else {
                                gnav_courses_button.focus = false;
                                gnav_courses_button.focusChanged(false);
                                gnav_courses_tooltip.hide();
                            }
                        }

                        onClicked: {

                        }

                        contentItem: Item {
                            Image {
                                id: gnav_courses_image
                                source: "qrc:/images/global_nav_courses.png";
                                width: 54;
                                height: 54;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_courses_text
                                z: gnav_courses_image.z + 1;
                                text: qsTr("Courses");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_courses_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_courses_tooltip.text
                                    font: gnav_courses_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }

                    Button {
                        id: gnav_calendar_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "View your calendar"

                        Accessible.name: "Calendar";
                        Accessible.description: button_text;
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if (hovered) {
                                gnav_calendar_button.focus = true;
                                gnav_calendar_button.forceActiveFocus();
                                gnav_calendar_button.focusChanged(true);
                                gnav_calendar_tooltip.show(button_text);
                            } else {
                                gnav_calendar_button.focus = false;
                                gnav_calendar_button.focusChanged(false);
                                gnav_calendar_tooltip.hide();
                            }
                        }

                        onClicked: {

                        }

                        contentItem: Item {
                            Image {
                                id: gnav_calendar_image
                                source: "qrc:/images/global_nav_calendar.png";
                                width: 54;
                                height: 54;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_calendar_text
                                z: gnav_calendar_image.z + 1;
                                text: qsTr("Calendar");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_calendar_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_calendar_tooltip.text
                                    font: gnav_calendar_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }

                    Button {
                        id: gnav_inbox_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "View your messages"

                        Accessible.name: "Inbox"
                        Accessible.description: "View your messages"
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if (hovered) {
                                gnav_inbox_button.focus = true;
                                gnav_inbox_button.forceActiveFocus();
                                gnav_inbox_button.focusChanged(true);
                                gnav_inbox_tooltip.show(button_text);
                            } else {
                                gnav_inbox_button.focus = false;
                                gnav_inbox_button.focusChanged(false);
                                gnav_inbox_tooltip.hide();
                            }
                        }

                        onClicked: {
                            appBreadCrumb.close();
                            appStack.replace(appInboxView);
                        }

                        contentItem: Item {
                            Image {
                                id: gnav_inbox_image
                                source: "qrc:/images/global_nav_inbox.png";
                                width: 54;
                                height: 54;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_inbox_text
                                z: gnav_inbox_image.z + 1;
                                text: qsTr("Inbox");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_inbox_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_inbox_tooltip.text
                                    font: gnav_inbox_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }

                    }


                    Button {
                        id: gnav_help_button
                        width: 84;
                        height: 84;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;

                        property string button_text: "Find help with common issues"

                        Accessible.name: "Help"
                        Accessible.description: button_text;
                        Accessible.role: Accessible.Button;
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if (hovered) {
                                gnav_help_button.focus = true;
                                gnav_help_button.forceActiveFocus();
                                gnav_help_button.focusChanged(true);
                                gnav_help_tooltip.show(button_text);
                            } else {
                                gnav_help_button.focus = false;
                                gnav_help_button.focusChanged(false);
                                gnav_help_tooltip.hide();
                            }
                        }

                        onClicked: {

                        }

                        contentItem: Item {
                            Image {
                                id: gnav_help_image
                                source: "qrc:/images/global_nav_help.png";
                                width: 54;
                                height: 54;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_help_text
                                z: gnav_help_image.z + 1;
                                text: qsTr("Help");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_help_tooltip
                                text: "";
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_help_tooltip.text
                                    font: gnav_help_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }

                    Button {
                        id: gnav_sync_w_canvas_button
                        width: 84;
                        height: 84;

                        //Accessible.enabled: true;
                        Accessible.name: "Sync"
                        Accessible.role: Accessible.Button;
                        Accessible.description: "Sync with Canvas Server (Only works when plugged in or on WiFi)"
                        Accessible.focusable: true;

                        onHoveredChanged: {
                            if (hovered) {
                                // Mouse hovering
                                gnav_sync_w_canvas_button.focus = true;
                                gnav_sync_w_canvas_button.forceActiveFocus();
                                gnav_sync_w_canvas_button.focusChanged(true);
                                //mainWidget.sendAccessibilityEvent(gnav_test_button, gnav_test_button.Accessible.role);
                                gnav_sync_w_canvas_tooltip.show(gnav_sync_w_canvas_button.Accessible.description);
                            } else {
                                // Mouse exited
                                gnav_sync_w_canvas_button.focus = false;
                                gnav_sync_w_canvas_button.focusChanged(false);
                                gnav_sync_w_canvas_tooltip.hide();
                            }
                            //console.log("Hovered: " + hovered);
                        }

                        onClicked: {
                            if (syncDrawer.position < 0.1) {
                                syncDrawer.open();
                            }
                        }


                        contentItem: Item {
                            Image {
                                id: gnav_sync_w_canvas_image
                                source: "qrc:/images/global_nav_sync.png";
                                width: 54;
                                height: 54;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                            }

                            Text {
                                id: gnav_sync_w_canvas_text
                                z: gnav_sync_w_canvas_image.z + 1;
                                text: qsTr("Sync");
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_sync_w_canvas_tooltip
                                text: gnav_sync_w_canvas_button.Accessible.description;
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;

                                contentItem: Text {
                                    text: gnav_sync_w_canvas_tooltip.text
                                    font: gnav_sync_w_canvas_tooltip.font
                                    color: "white";
                                }
                            }
                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }
                    }


                    // Filler item - there to take up space that is left and push buttons up to the top
                    Rectangle {
                        width: 84;
                        height: 84;
                        Layout.fillHeight: true;
                        Layout.preferredHeight: height;
                        Layout.preferredWidth: width;
                        color: App.global_nav_background;
                    }


                    Button {
                        id: gnav_minimize_button
                        width: 84;
                        height: 44;
                        Layout.preferredWidth: width;
                        Layout.preferredHeight: height;
                        Layout.alignment: Qt.AlignTop;
                        //color: App.global_nav_background;
                        //activeFocusOnTab: true;
                        //focus: true;

                        property string button_text: "Shrink global navigation menu"

                        Accessible.role: Accessible.Button;
                        Accessible.name: "Minimize";
                        Accessible.description: button_text;
                        Accessible.focusable: true;
                        //Accessible.onPressAction: gnav_sync_mousearea.clicked();
                        onHoveredChanged: {
                            if (hovered) {
                                // Mouse hovering
                                gnav_minimize_button.focus = true;
                                gnav_minimize_button.forceActiveFocus();
                                gnav_minimize_button.focusChanged(true);
                                gnav_minimize_tooltip.show(button_text);
                            } else {
                                // Mouse exited
                                gnav_minimize_button.focus = false;
                                gnav_minimize_button.focusChanged(false);
                                gnav_minimize_tooltip.hide();
                            }
                            //console.log("Hovered: " + hovered);
                        }
                        onClicked: {
                            global_nav_sidebar.state = "closed";
                            global_nav_sidebar_maximize.state = "open";
                        }

                        contentItem: Item {
                            Image {
                                id: gnav_minimize_image
                                source: "qrc:/images/global_nav_minimize.png";
                                width: 34;
                                height: 34;
                                fillMode: Image.PreserveAspectFit;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                anchors.verticalCenter: parent.verticalCenter;
                            }

                            Text {
                                id: gnav_minimize_text
                                z: gnav_minimize_image.z + 1;
                                text: "" // gnav_minimize_button.Accessible.name
                                color: App.global_nav_text;
                                //font.bold: true;
                                font.family: App.global_font_family;
                                font.pixelSize: App.global_font_size;
                                anchors.bottom: parent.bottom;
                                anchors.horizontalCenter: parent.horizontalCenter;
                                bottomPadding: 12;
                            }

                            ToolTip {
                                id: gnav_minimize_tooltip
                                text: gnav_minimize_button.button_text;
                                visible: false;
                                font.pointSize: 14
                                font.bold: true;
                                //focus: true;


                                contentItem: Text {
                                    text: gnav_minimize_tooltip.text
                                    font: gnav_minimize_tooltip.font
                                    color: "white";
                                }
                            }

                        }

                        background: Rectangle {
                            width: 84;
                            height: 84;
                            Layout.preferredWidth: width;
                            Layout.preferredHeight: height;
                            Layout.alignment: Qt.AlignTop;
                            color: parent.hovered ? App.global_nav_background_hover : App.global_nav_background;
                        }

                    }

                }

            }


            ColumnLayout {
                // Breadcrumb
                Rectangle {
                    id: appBreadCrumb;
                    height: 43; // TODO - Put this back when you want to see it 43;
                    width: parent.width;
                    Layout.fillWidth: true;
                    Layout.preferredHeight: height;
                    implicitHeight: height;
                    visible: false;
                    color: "white";

                    signal itemClicked(int index);

                    function addBCrumbItem(text, view, key) {
                        crumbView.model.append({ label: text, view: view, key: key });
                    }
                    function removeBCrumbItem() {
                        var model = crumbView.model;
                        if (model.count > 0) {
                            model.remove(model.count - 1);
                        }
                    }
                    function removeLowerCrumbItems(index) {
                        // Remove crumbs past the current index position
                        while ((crumbView.model.count - 1) > index) {
                            appBreadCrumb.removeBCrumbItem();
                        }
                    }
                    function removeAllCrumbItems() {
                        while (crumbView.model.count > 0) {
                            appBreadCrumb.removeBCrumbItem();
                        }
                    }
                    function close() {
                        appBreadCrumb.visible = false;
                    }
                    function open() {
                        appBreadCrumb.visible = true;
                    }
                    function setBreadCrumbs(arr) {
                        appBreadCrumb.removeAllCrumbItems();
                        //arr.forEach(element, appBreadCrumb.addBCrumbItem(element.label, element.view, element.key));
                        for (let i = 0; i < arr.length; i++) {
                            appBreadCrumb.addBCrumbItem(arr[i].label, arr[i].view, arr[i].key);
                        }

                        appBreadCrumb.open();
                        //appBreadCrumb.addBCrumbItem("Assignments", "Assignments", "Assignments")
                    }

                    ListView {
                        id: crumbView
                        anchors.fill: parent;
                        anchors.margins: 10;
                        orientation: ListView.Horizontal;

                        model: ListModel {
//                            ListElement {
//                                label: "Test";
//                                view: "test";
//                                key: "Test";
//                            }
                        }

                        delegate: Rectangle {
                            id: crumbItem;
                            color: "white"
                            width: itemText.paintedWidth + 20;
                            height: crumbView.height;
                            clip: true;

                            function getText(val, index, length) {
                                var ret_text = "";
                                if (index > 0) {
                                    // Not the first item, add the >
                                    ret_text += "<font color='#000000'>&gt;</font> ";
                                }

                                if (typeof val === 'undefined') {
                                    val = "(undefined)";
                                    val = "";
                                }

                                // If this is the last item, then color should be black
                                //console.log('ind ' + index + " len " + length);
                                //if (index === length-1) {
                                    ret_text += "<font color='#000000'>" + val + "</font>"
                                //} else {
                                    // Do this part if making course clickable
                                //    ret_text += "<a href='click://course/" + val + "/" + "'>" + val + "</a>";
                                //}

                                return ret_text;
                            }

                            Text {
                                id: itemText;
                                anchors.verticalCenter: parent.verticalCenter;
                                //x: 10;
                                color: App.global_link_color;
                                text: getText(label, index, crumbView.model.count);
                                font.pixelSize: 18;
                                font.family: "Lato Extended";
                                textFormat: Text.RichText;
                                onLinkActivated: (link) => {
                                    console.log("Clicked " + link);
                                    appBreadCrumb.itemClicked(link);
                                }
                            }

//                            MouseArea {
//                                anchors.fill: parent;
//                                hoverEnabled: true;
//                                onClicked: {
//                                    appBreadCrumb.removeLowerCrumbItems(index);
//                                    appBreadCrumb.itemClicked(index);
//                                }
//                            }

                            // Animations
//                            ListView.onAdd: SequentialAnimation {
//                                PropertyAction { target: delegate; property: "ListView.delayRemove"; value: true }
//                                PropertyAction { target: delegate; property: "width"; value: 0 }
//                                NumberAnimation { target: delegate; property: "width"; to: fullWidth; duration: 250 }
//                                PropertyAction { target: delegate; property: "ListView.delayRemove"; value: false }
//                            }
//                            ListView.onRemove: SequentialAnimation {
//                                PropertyAction { target: delegate; property: "ListView.delayRemove"; value: true }
//                                NumberAnimation { target: delegate; property: "width"; to: 0; duration: 250 }
//                                PropertyAction { target: delegate; property: "ListView.delayRemove"; value: false }
//                            }
                        }


                    }


                }


                // Main Page Area
                RowLayout {
                    // Course Menu Sidebar
                    Rectangle {
                        id: appSideBarParent;
                        width: 0; // start minimized 180
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        Layout.preferredWidth: width
                        Layout.preferredHeight: 200
                        Layout.minimumWidth: width
                        Layout.maximumWidth: width
                        clip: true;
                        //color: "#eeeeee"

                        property bool isOpen: false;

                        states: [
                            State {
                                name: "open";
                                when: appSideBarParent.isOpen;
                                PropertyChanges {
                                    target: appSideBarParent;
                                    width: 180;
                                }
                            },
                            State {
                                name: "closed";
                                when: !appSideBarParent.isOpen;
                                PropertyChanges {
                                    target: appSideBarParent;
                                    width: 0;
                                }
                            }

                        ]

                        transitions: Transition {
                            NumberAnimation {
                                properties: "width";
                                easing.type: Easing.InOutQuad;
                                duration: 450;
                            }
                        }


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
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Assignments", view: "Assignments", key: "Assignments"}
                                                ]);

                                            appStack.replace(appAssignmentsListView);
                                            break;
                                        case "Modules":
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Modules", view: "Modules", key: "Modules"}
                                                ]);
                                            appStack.replace(appModulesListView);
                                            break;
                                        case "Pages":
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Pages", view: "Pages", key: "Pages"}
                                                ]);
                                            appStack.replace(appPagesView);
                                            break;
                                        case "Files":
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Files", view: "Files", key: "Files"}
                                                ]);
                                            appStack.replace(appFilesView);
                                            break;
                                        case "Announcements":
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Announcements", view: "Announcements", key: "Announcements"}
                                                ]);
                                            appStack.replace(appAnnouncementsView);
                                            break;
                                            // Inbox isn't available inside courses?
                                            //                                case "Inbox":
                                            //                                    appStack.replace(appInboxView);
                                            //                                    break;
                                        case "Quizzes":
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Quizzes", view: "Quizzes", key: "Quizzes"}
                                                ]);
                                            appStack.replace(appQuizzesView);
                                            break;
                                        case "Discussions":
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id },
                                                {label: "Discussions", view: "Discussions", key: "Discussions"}
                                                ]);
                                            appStack.replace(appDiscussionsView);
                                            break;
                                        default:
                                            appBreadCrumb.setBreadCrumbs([
                                                {label: main_window.current_course_code, view: "Course", key: main_window.current_course_id }
                                                ]);
                                            appStack.replace(appHomePageView);
                                            //appStack.replace(appDashboardView);
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

                            initialItem: appDashboardView //appHomePageView
                        }
                    }

                }

            }

            }




    }




    Component {
        id: appDashboardView
        AppDashboardPage {
            global: main_window;

            onCourseClicked: (course_id, course_name, course_code) => {
                console.log("Course Clicked: " + course_id);
                main_window.current_course_id = course_id;
                main_window.current_course_name = course_name;
                main_window.current_course_code = course_code;
                main_window.current_page_url = "";
                main_window.current_assignment_id = "";

                appBreadCrumb.setBreadCrumbs([
                    {label: course_code, view: "Course", course_id}
                    ]);
                appStack.replace(appHomePageView);
            }
            Component.onCompleted: {
                console.log("appDashboardView onComplete...");
                appSideBarParent.isOpen = false;
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

            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
        }
    }

    Component {
        id: appWikiPageView
        AppWikiPage {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_page_url: main_window.current_page_url;
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
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
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
        }
    }

    Component {
        id: appFilesView
        AppFiles {
            global: main_window;
            current_course_id: main_window.current_course_id
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
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
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
        }
    }


    Component {
        id: appAssignmentPage
        AppAssignmentPage {
            global: main_window;
            current_course_id: main_window.current_course_id;
            current_assignment_id: main_window.current_assignment_id;
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
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
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
        }
    }

    Component {
        id: appAnnouncementsView
        AppAnnouncements {
            global: main_window;
            current_course_id: main_window.current_course_id;
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
        }
    }

    Component {
        id: appInboxView
        AppInbox {
            global: main_window;
            current_course_id: main_window.current_course_id;
            Component.onCompleted: {
                appSideBarParent.isOpen = false;
            }
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
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
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
            Component.onCompleted: {
                appSideBarParent.isOpen = true;
            }
        }
    }


    Drawer {
        id: syncDrawer
        y: appPage.y
        width: appPage.width - appPage.gnav_width // * 0.99
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
