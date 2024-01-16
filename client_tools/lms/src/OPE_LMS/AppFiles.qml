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

    padding: 3

    Component.onCompleted:  {
        loadFiles();
    }

    function loadFiles() {
        // Load the list of Folders

        //var m = filesList.model
        //m.modifyFilter("course_id=" + App.current_course)
        //m.select()
        var m = file_folders_query; //foldersList.model;
        m.modifyFilter("course_id=" + current_course_id);
        m.sortOn("sort_order");
        m.refresh();

    }

    header: Text {
        text: "Course Files"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: App.text_color;
    }

    ListView {
        id: filesList
        width: parent.width
        height: parent.height
        interactive: true
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false
        clip: true

        ScrollBar.vertical: ScrollBar {}

        //model: files_model
        model: file_folders_query

        section.property: "name"
        section.criteria: ViewSection.FullString
        section.delegate: Component {
            id: sectionHeading
            Rectangle {
                width: parent.width
                height: childrenRect.height
                color: App.section_bg_color;
                radius: 3
                Text {
                    height: 30
                    text: section
                    font.bold: true
                    font.pixelSize: 17
                    color: App.section_text_color;
                    padding: 4;
                    leftPadding: 12;
                }
            }
        }

        highlight: Rectangle {
            width: filesList.width;
            height: 30
            color: App.highlight_color; // "lightgrey"
            radius: 3
            opacity: 0;
        }

        delegate: Component {
            Rectangle {
                id: item
                Layout.fillWidth: true
                width: filesList.width
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
                        text: display_name
                        font.pixelSize: 14
                        color: App.text_color;
                        padding: 3;
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: { parent.color=App.highlight_color; }
                    onExited: { parent.color=App.bg_color; }
                    onClicked: {
                        var item_name = App.getFieldValue(filesList.model, index, "display_name");
                        var pull_file = App.getFieldValue(filesList.model, index, "pull_file");
                        if (pull_file === "") {
                            console.log("File not downloaded! " + item_name);
                            return;
                        }
                        var local_url = pull_file;

                        console.log("Loading file: " + item_name);
                        // TODO - load file
                        //loadPage(item_url);
                        mainWidget.desktopLaunch(local_url);

                    }
                }
            }
        }
    }
}

