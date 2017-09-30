import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.2
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    id: modulesPage
    signal refreshPage();
    signal loadPage(string page_url);

    onRefreshPage: {
        console.log("RefreshModulesCalled");
        loadModules();
    }
    Component.onCompleted:  {
        loadModules();
    }

    function loadModules() {
        // Load the list of modules with sub items
        var m = modulesList.model
        m.modifyFilter("course_id=" + App.current_course)

    }

    header: Text {
        text: "Modules Screen"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
    }

    ListView {
        id: modulesList
        width: parent.width
        height: parent.height
        interactive: false
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false

        model: module_items_query

        section.property: "name"
        section.criteria: ViewSection.FullString
        section.delegate: Component {
            id: sectionHeading
            Rectangle {
                width: parent.width
                height: childrenRect.height
                color: "steelblue"
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
                        var item_type = App.getFieldValue(modulesList.model, index, "type");
                        switch (item_type) {
                        case "File":
                            // Need to lookup the file info
                            // Split on the full url to get the file id
                            var parts = full_url.split("/");
                            var file_id = parts[parts.length-1];
                            var fm = files_model
                            fm.modifyFilter("id=" + file_id)
                            var local_url = App.getFieldValue(fm, 0, "pull_file");
                            if (local_url == "") {
                                console.log("File not downloaded!");
                                return;
                            }
                            local_url = "file:///" + mainWidget.fileCacheFolder() + local_url
                            console.log("Loading File: " + local_url);
                            mainWidget.desktopLaunch(local_url);
                            break;
                        case "Page":
                            console.log("Loading Page: " + item_url);
                            loadPage(item_url);

                            break;
                        default:
                            console.log("Unknown type!");
                        }

                        //console.log("ItemClick: " + App.getFieldValue(modulesList.model, index, "type"));
                    }
                }
            }
        }
    }
}
