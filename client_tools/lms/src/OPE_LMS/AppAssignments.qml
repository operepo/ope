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

Page {
    property QtObject global;

    property string current_course_id: "";
    property string current_assignent_id: "";

    signal assignmentClicked(string assignment_id);

    padding: 3

    onCurrent_course_idChanged: {
        loadAssignments();
    }

    Component.onCompleted:  {
        loadAssignments();
    }

    function loadAssignments() {
        // Load the list of Assignments
        var m = assignmentsList.model;
        m.modifyFilter("course_id=" + current_course_id);
        m.sortOn("position");
        m.select();

    }

    header: Text {
        text: "Assignments"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: App.text_color;
    }

    ListView {
        id: assignmentsList
        width: parent.width
        height: parent.height
        interactive: true
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false
        clip: true;

        ScrollBar.vertical: ScrollBar {}

        model: assignments_model

        highlight: Rectangle {
            width: assignmentsList.width;
            height: 30
            color: App.highlight_color;
            radius: 3
            opacity: 0
        }

        delegate: Component {
            Rectangle {
                id: item
                Layout.fillWidth: true
                width: assignmentsList.width
                height: 30
                implicitHeight: height
                color: App.bg_color;
                radius: 3
                //opacity: 0.5
                property int indexOfThisDelegate: index;

                Row {
                    Text {
                        height: 30
                        verticalAlignment: Text.AlignVCenter
                        text: name
                        color: App.text_color;
                        font.pixelSize: 14;
                        padding: 3;
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: { parent.color=App.highlight_color; }
                    onExited: { parent.color=App.bg_color; }
                    onClicked: {
                        var assignment_id = App.getFieldValue(assignmentsList.model, index, "id");
                        console.log("Assignment clicked..." + assignment_id);
                        global.current_assignment_id = assignment_id;
                        assignmentClicked(assignment_id);
                    }
                }
            }
        }
    }
}
