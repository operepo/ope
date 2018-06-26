import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2
import QtQuick.Controls.Universal 2.2
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3


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
                        width: 32
                        height: 32
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

                            onClicked: {
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











    Drawer {
        id: syncDrawer
        y: appPage.y
        width: appPage.width // * 0.99
        height: appPage.height
        edge: Qt.RightEdge
        dragMargin: 0

        AppSyncPage {
            anchors.fill: parent;
        }

    }



}
