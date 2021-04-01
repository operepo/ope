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


Item {
    id: appSideBarRoot
    anchors.fill: parent;

    signal clicked(string tab_name);

    function selectMenuTab(tab_name) {
        // Find the tab in question, select it, and
        // fire the clicked tab
        var tab_index = 0;
        var m = courseTabs.model;

        for(var i=0; i < m.count; i++) {
            var item = m.get(i);
            if (item.name === tab_name) {
                //console.log("Found Tab Index");
                tab_index = i;
            }
        }
        if (courseTabs.currentIndex != tab_index) {
            courseTabs.currentIndex = tab_index;
            // Fire click event
            clicked(tab_name);
        }
    }

    ListView {
        width: parent.width
        height: parent.height
        id: courseTabs
        interactive: true
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: true


        ScrollBar.vertical: ScrollBar {}

        highlight: Rectangle {
            width: parent.width
            height: 30
            color: App.highlight_color;
            radius: 3
        }


        delegate: Component {
            Rectangle {
                id: item
                Layout.fillWidth: true
                width: parent.width
                height: 30
                implicitHeight: height
                color: App.bg_color;
                radius: 3
                //opacity: 0.5
                property int indexOfThisDelegate: index


                Row {
                    Text {
                        height: 30
                        verticalAlignment: Text.AlignVCenter
                        text: name
                        color: App.text_color;
                        font.bold: true
                        font.pixelSize: 18
                        padding: 6
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: { parent.color=App.highlight_color; }
                    onExited: { parent.color=App.bg_color; }
                    onClicked: {
                        // Set the current tab
                        courseTabs.currentIndex = indexOfThisDelegate
                        // Load the page
                        //pageLoader.setSource(name + ".qml");
                        appSideBarRoot.clicked(name);

                    }
                }
            }
        }

        model: ListModel {
            id: courseTabsModel
            ListElement { name: "Home"; order: 0; enabled: true }
            ListElement { name: "Modules"; order: 1; enabled: true }
            ListElement { name: "Pages"; order: 2; enabled: true }
            ListElement { name: "Assignments"; order: 3; enabled: true }
            //ListElement { name: "Quizzes"; order: 4; enabled: true }
            ListElement { name: "Inbox"; order: 5; enabled: true }
            //ListElement { name: "Calendar"; order: 6; enabled: false }
            ListElement { name: "Announcements"; order: 7; enabled: false }
            //ListElement { name: "Discussions"; order: 8; enabled: false }
            //ListElement { name: "Grades"; order: 9; enabled: false }
            ListElement { name: "Files"; order: 10; enabled: true }
            ListElement { name: "Syllabus"; order: 11; enabled: true }

        }
    }

}
