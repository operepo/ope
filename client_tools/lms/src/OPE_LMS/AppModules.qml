import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.3
import QtQuick.Controls.Universal 2.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2

import com.openprisoneducation.ope 1.0
import "App.js" as App


Page {
    id: modulesPage

    property QtObject global;

    property string current_course_id: "";
    property string current_assignment_id: "";
    property string current_page_url: "";

    // Module items can be File, Page, Discussion, Assignment,
    // Quiz, SubHeader, ExternalUrl, ExternalTool
    signal moduleFileClicked(string file_id);
    signal modulePageClicked(string page_url);
    signal moduleDiscussionClicked(string discussion_id);
    signal moduleAssignmentClicked(string assignment_id);
    signal moduleQuizClicked(string quiz_id);
    signal moduleSubHeaderClicked(string sub_header_id);
    signal moduleExternalUrlClicked(string external_url);
    signal moduleExternalToolClicked(string external_tool);

    padding: 3;


    Component.onCompleted:  {
        loadModules();
    }

    function loadModules() {
        // Load the list of modules with sub items
        var m = module_items_query; //modulesList.model
        m.modifyFilter("course_id=" + current_course_id);
        m.sortOn("CAST(sort_order1 as unsigned), CAST(sort_order2 as unsigned)");
        //m.sortOn("position");
        m.refresh();
    }

    header: Text {
        text: "Modules Screen"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: "steelblue"
    }

    ListView {
        id: modulesList
        anchors.fill: parent
        //width: parent.width
        //height: parent.height
        interactive: true
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false
        clip: true;

        ScrollBar.vertical: ScrollBar {}

        model: module_items_query

        section.property: "name"
        section.criteria: ViewSection.FullString
        section.delegate: Component {
            id: sectionHeading
            Rectangle {
                width: parent.width
                height: childrenRect.height
                color: "lightsteelblue"
                radius: 3
                Text {
                    height: 30
                    text: section
                    font.bold: true
                    font.pixelSize: 17
                }
            }
        }

        highlight: Rectangle {
            width: modulesList.width;
            height: 30
            color: "lightgrey"
            radius: 3
            opacity: 0;
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
                        text: title
                        font.pixelSize: 14
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: { parent.color="lightsteelblue" }
                    onExited: { parent.color="lightgrey" }
                    onClicked: {
                        var item_url = App.getFieldValue(modulesList.model, index, "page_url");
                        var full_url = App.getFieldValue(modulesList.model, index, "url");
                        var html_url = App.getFieldValue(modulesList.model, index, "html_url");
                        var item_type = App.getFieldValue(modulesList.model, index, "type");
                        var content_id = App.getFieldValue(modulesList.model, index, "content_id");
                        switch (item_type) {
                        case "File":
                            // Need to lookup the file info
                            // Split on the full url to get the file id
                            var parts = full_url.split("/");
                            var file_id = parts[parts.length-1];
                            var fm = files_model
                            fm.modifyFilter("id=" + file_id)
                            var local_url = App.getFieldValue(fm, 0, "pull_file");
                            if (local_url === "") {
                                console.log("File not downloaded!");
                                return;
                            }
                            // desktopLaunch already deals with fileCacheFolder
                            console.log("Loading File: " + local_url);
                            mainWidget.desktopLaunch(local_url);
                            break;
                        case "Page":
                            console.log("Loading Page: " + item_url);
                            //loadPage(item_url);
                            global.current_page_url = item_url;
                            modulePageClicked(item_url);

                            break;
                        case "Assignment":
                            console.log("Assignment clicked " + content_id);
                            global.current_assignment_id = content_id;
                            moduleAssignmentClicked(content_id);
                            break;
                        default:
                            alertPopup.title = "Not Implemented Yet!";
                            alertPopup.text = 'Not Implemented Yet!\nQuizzes and other features may not be ready yet, please be patient.';
                            alertPopup.visible = true;
                            console.log("Module Item - Unknown type - Not Implemented Yet!");
                        }

                        //console.log("ItemClick: " + App.getFieldValue(modulesList.model, index, "type"));
                    }
                }
            }
        }

        MessageDialog {
            id: alertPopup
            title: ""
            text: ""
            onAccepted: {
                visible = false;
            }
        }
    }
}


