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
    signal refreshPage();
    signal loadPage(string page_url);

    onRefreshPage: {
        console.log("RefreshPagesCalled");
        loadPages();
    }
    Component.onCompleted:  {
        loadPages();
    }

    function loadPages() {
        // Load the list of pages
        var m = pagesList.model
        m.modifyFilter("course_id=" + App.current_course)
        m.select()

    }

    header: Text {
        text: "Pages Screen"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
    }

    ListView {
        id: pagesList
        width: parent.width
        height: parent.height
        interactive: false
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false


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
                        console.log("Loading Page: " + item_url);
                        loadPage(item_url);
                    }
                }
            }
        }
    }
}
