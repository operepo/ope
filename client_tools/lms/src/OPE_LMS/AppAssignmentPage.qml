import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Universal 2.15
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.15
import QtQuick.Layouts 1.15

import QtWebView 1.1


import com.openprisoneducation.ope 1.0
import "App.js" as App


Page {
    property QtObject global;
    property string current_course_id: "";
    property string current_assignment_id: "";


    function loadAssignment() {
        console.log("  - loadAssignment: " +  current_assignment_id);
        var m = assignments_model.copy();
        m.modifyFilter("id='" + current_assignment_id + "'");
        m.select();

        var a_name = "ASSIGNMENT NAME";
        var a_desc = "ASSIGNMENT DESCRIPTION";
        for(var i = 0; i < m.rowCount(); i++) {
            a_name = App.getFieldValue(m, i, "name").toString();
            a_desc = App.getFieldValue(m, i, "description").toString();
        }

        // Add injected javascript to page
        a_desc += "\n" + App.WebChannelJS;
        //console.log("<<< PAGE: " + a_desc);

        //a_desc = "TEST DESC";
        //descTest.text = a_desc;
        //assignmentName.text = a_name;
        headerText.text = "Assignment - " + a_name;
        assignmentDescription.loadHtml(a_desc);
        // Inject webchannel stuff into page
        //console.log("JS " + App.WebChannelJS);
        //assignmentDescription.runJavaScript(App.WebChannelJS,
        //                                    function(result) {
        //                                        console.log(">>> runJavascript: " + result);
        //                                    });

        //assignmentDescription.runJavaScript("alert('hi!');",
        //                                    function(result) {
        //                                        alert('RESULT ' + result);
        //                                    });

        // Load the assignment_submissions
        m = assignment_submissions_model
        m.modifyFilter("assignment_id='" + current_assignment_id + "'");
        m.select();

        // Webengine - need to write jscript to set the page
        //App.setHTML(webView, page);
        //webView.loadHtml(page);
    }

    Component.onCompleted: {

        loadAssignment();


    }

    header: Text {
        id:headerText
        text: "Assignment"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        wrapMode: Text.Wrap;
        color: App.text_color;
    }

    contentData: Flickable {
        anchors.fill:  parent

        ScrollBar.vertical: ScrollBar {}


        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // Assignment instructions part
            Rectangle {
                Layout.fillHeight: true;
                Layout.minimumHeight: 200
                Layout.fillWidth: true;
                Layout.minimumWidth: 50
                Layout.preferredWidth: parent.width

                WebView {
                    anchors.fill:  parent
                    //width: parent.width
                    //height: 60;

                    id: assignmentDescription
                    focus: true
                    //loadProgress: 0


                    onLoadingChanged: {
                        var err = loadRequest.errorString
                        var status = loadRequest.status
                        //console.log("Loading changed..." + status)
                    }

                }
            }

            // Button to open submission area
            Rectangle {
                id: submissionButton
                Layout.fillHeight: false;
                Layout.minimumHeight: 48
                Layout.maximumHeight: 48
                Layout.fillWidth: true;
                Layout.minimumWidth: 50
                Layout.preferredWidth: parent.width
                color: "white"
                RowLayout {
                    anchors.fill: parent

                    Image {
                        id: submissionDrawerButtonImage
                        Layout.minimumHeight: parent.implicitHeight
                        Layout.minimumWidth: paintedWidth
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                        source: submissionDrawer.is_open ? "qrc:/images/down_arrow.png" : "qrc:/images/up_arrow.png"
                        width: 48
                        height: 48
                        fillMode: Image.PreserveAspectFit


                    }
                    Text {
                        id: submissionDrawerButtonText
                        Layout.minimumHeight: parent.implicitHeight
                        //height: 35
                        verticalAlignment: Text.AlignVCenter
                        Layout.minimumWidth: 60
                        Layout.maximumWidth: Layout.minimumWidth
                        Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        text: "Submissions"
                        font.bold: true
                        color: "black"
                        font.pointSize: 14
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true;

                    onEntered: {
                        submissionButton.color = "lightsteelblue"
                    }
                    onExited:  {
                        submissionButton.color = "white";
                    }

                    onClicked: {
                        submissionDrawer.is_open = submissionDrawer.is_open ? false : true;
                    }

                }

            }

            // Submissions Area
            Rectangle {
                id: submissionDrawer
                property bool is_open: false;
                property int drawerOpenHeight: 200
                Layout.fillHeight: false;
                implicitHeight: 0
                Layout.minimumHeight: 0
                Layout.maximumHeight: drawerOpenHeight
                Layout.fillWidth: true;
                Layout.minimumWidth: 50
                Layout.preferredWidth: parent.width

                onIs_openChanged: {
                    // Open or close the drawer
                    console.log("is_open_changed");
                    submissionDrawer.implicitHeight = is_open ? drawerOpenHeight : 0;
                }

                Behavior on implicitHeight {
                    SmoothedAnimation {
                        velocity: 400;
                    }

                }

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    // Turn in tabs
                    TabBar {
                        id: assignmentsTurnInTabs
                        Layout.minimumHeight: 30
                        Layout.maximumHeight: 30
                        Layout.fillWidth: true
                        Layout.minimumWidth: 50
                        //width: parent.implicitWidth
                        //height: 30;
                        //implicitHeight: height;
                        contentHeight: 30


                        TabButton {
                            text: "File Upload"
                        }
                        TabButton {
                            text: "Text Entry"
                        }
                        TabButton {
                            text: "Quizz"
                            visible: false;
                            width: visible ? parent.width / 4 : 0;

                        }

                        TabButton {
                            text: "Submissions"
                        }

                    }

                    SwipeView {
                        Layout.minimumHeight: 90
                        Layout.maximumHeight: submissionDrawer.drawerOpenHeight - assignmentsTurnInTabs.implicitHeight
                        Layout.fillWidth: true
                        Layout.minimumWidth: 50
                        Layout.fillHeight: true
                        //anchors.fill: parent
                        currentIndex: assignmentsTurnInTabs.currentIndex
                        clip: true;

                        // File Upload Tab
                        Rectangle {
                            //anchors.fill: parent
                            color: "blue"

                            Text {
                                text: "Drop Assignment Here!"
                                font.bold: true
                                font.pointSize: 20
                                anchors.fill: parent
                                verticalAlignment: Qt.AlignVCenter
                                horizontalAlignment: Qt.AlignHCenter
                            }
                            Image {
                                source: "/images/upload_file.png"
                                width: 60
                                height: 60
                            }

                            DropArea {
                                id: assignmentDrop
                                anchors.fill: parent

                                //keys: ["text/plain", ]
                                onDropped: {
                                    // Pull current info for the assignment
                                    var m = assignments_model.copy();
                                    m.modifyFilter("id='" + current_assignment_id + "'");
                                    m.select();

                                    var course_id = "0";
                                    var assignment_id = "0";

                                    for(var i = 0; i < m.rowCount(); i++) {
                                        assignment_id = App.getFieldValue(m, i, "id").toString();
                                        course_id = App.getFieldValue(m, i, "course_id").toString();
                                    }

                                    console.log("drop hastext " + drop.hasText + " - " + drop.text)
                                    console.log("Drop action " + drop.proposedAction)
                                    console.log(drop.urls)
                                    console.log("Source "+ drop.source)
                                    //console.log("Formats " + drop.formats)

                                    var txt_answer = ""; // Should be blank if dropping a file
                                    var file_url = "";

                                    if (drop.urls.length > 0) {
                                        file_url = drop.urls[0];
                                    }
                                    console.log("-- Course id: " + course_id);
                                    console.log("-- Assignemnt id: " + assignment_id);
                                    var ret = mainWidget.canvas.queueAssignmentFile(course_id, assignment_id, txt_answer, file_url);
                                    if (!ret) {
                                        console.log("ERROR - Couldn't queue assignment file!");
                                    }
                                }
                            }
                        }

                        // Text Entry Tab
                        Rectangle {
                            color: "lightsteelblue"
                            border.color: "#dddddd"
                            border.width: 1
                            //anchors.fill: parent
                            Column {
                                anchors.fill: parent
                                Text {
                                    text: "Type Submission Here"
                                }

                                TextArea {
                                    id: textTurnIn
                                    width: parent.width
                                    height: parent.height - textTurnInComment.height

                                }
                                Text {
                                    text: "Comments:"
                                }

                                TextArea {
                                    id: textTurnInComment
                                    width: parent.width
                                    height: 15

                                }
                            }



                        }

                        // Quizzes Tab
                        Rectangle {
                            Text {
                                text: "Quizzes not implemented yet"
                            }
                        }

                        // List of submitted assignments
                        Rectangle {
                            //anchors.fill:  parent
                            // Location of submtted assignment
                            ListView {
                                id: submittedAssignments
                                anchors.fill: parent
                                interactive: true
                                focus: false
                                spacing: 4
                                ScrollBar.vertical: ScrollBar {}

                                model: assignment_submissions_model

                                header: Component {
                                    Text {
                                        text: "Current Submissions"
                                        font.bold: true
                                        font.pointSize: 9
                                    }
                                }

                                highlight: Rectangle {
                                    width: submittedAssignments.width;
                                    height: 15
                                    color: "steelblue"
                                    radius: 3
                                    opacity: 0
                                }

                                delegate: Component {
                                    Rectangle {
                                        id: item
                                        Layout.fillWidth: true;
                                        width: parent.width;
                                        height: 15;
                                        implicitHeight: height;
                                        color: "lightgrey"
                                        radius: 3
                                        opacity: 0.5
                                        property int indexOfThisDelgate: index;

                                        Row {
                                            Text {
                                                height: 15
                                                verticalAlignment: Text.AlignVCenter;
                                                text: queued_on
                                                font.pixelSize: 8
                                            }
                                        }
                                    }
                                }
                            }
                        }

                    }



                }




            }


        }

    }

}
