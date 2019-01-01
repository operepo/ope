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
    property string current_page_url: "";
    property string current_course_id: "";

    signal pageClicked(string page_url);

    padding: 3


    Component.onCompleted:  {
        loadCanvasWikiPages();
    }

    function loadCanvasWikiPages() {
        // Load the list of pages
        var m = pagesList.model;
        m.modifyFilter("course_id=" + current_course_id);
        m.sortOn("title");
        m.select();

    }

    header: Text {
        text: "Canvas Pages"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: "steelblue"
    }

    ListView {
        id: pagesList
        width: parent.width
        height: parent.height
        interactive: true
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false
        clip: true;

        ScrollBar.vertical: ScrollBar {}

        model: pages_model

        highlight: Rectangle {
            width: pagesList.width;
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
                        var item_url = App.getFieldValue(pagesList.model, index, "url");
                        global.current_page_url = item_url;
                        pageClicked(item_url);
                    }
                }
            }
        }
    }
}
