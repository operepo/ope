import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.3
import QtQuick.Controls.Universal 2.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3

//import QtWebView 1.1
import QtWebEngine 1.4

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    signal refreshPage();
    signal loadPage(string page_url, string page_type);
    padding: 3

    onRefreshPage: {
        console.log("RefreshPagesCalled");
        loadAssignments();
    }
    Component.onCompleted:  {
        loadAssignments();
    }

    function loadAssignments() {
        // Load the list of Assignments
        var m = assignmentsList.model;
        m.modifyFilter("course_id=" + App.current_course);
        m.sortOn("position");
        m.select();

    }

    header: Text {
        text: "Assignments"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
    }

    ListView {
        id: assignmentsList
        width: parent.width
        height: parent.height
        interactive: false
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false
        clip: true;

        ScrollBar.vertical: ScrollBar {}

        model: assignments_model

        highlight: Rectangle {
            width: assignmentsList.width;
            height: 30
            color: "steelblue"
            radius: 3
            opacity: 0
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
                property int indexOfThisDelegate: index;

                Row {
                    Text {
                        height: 30
                        verticalAlignment: Text.AlignVCenter
                        text: name
                        font.pixelSize: 14
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: { parent.color="lightsteelblue" }
                    onExited: { parent.color="lightgrey" }
                    onClicked: {
                        var item_url = App.getFieldValue(assignmentsList.model, index, "html_url");
                        console.log("Loading Assignment: " + item_url);
                        // TODO - load assignment
                        loadPage(item_url, "AssignmentPage");
                        console.log("Assignment clicked...");
                    }
                }
            }
        }
    }
}
