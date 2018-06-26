import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2
import QtQuick.Controls.Universal 2.2
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3

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
        color: "steelblue"
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
