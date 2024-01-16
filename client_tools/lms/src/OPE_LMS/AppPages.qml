import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Controls.Universal
//import QtQuick.Controls.Styles
import QtQuick.Controls.Imagine
import QtQuick.Layouts

import QtWebView 1.1

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
        text: "Pages"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: App.text_color;
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
            color: App.highlight_color;
            radius: 3
            opacity: 0
        }

        delegate: Component {
            Rectangle {
                id: item
                Layout.fillWidth: true
                width: pagesList.width
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
                        text: title
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
                        var item_url = App.getFieldValue(pagesList.model, index, "url");
                        global.current_page_url = item_url;
                        pageClicked(item_url);
                    }
                }
            }
        }
    }
}
