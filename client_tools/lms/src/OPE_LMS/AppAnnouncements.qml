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

    id: announcemntsPage

    property QtObject global;

    property string current_course_id: "";


    header: Text {
        text: "Announcements"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: "steelblue"
    }
    padding: 3

    onCurrent_course_idChanged: {
        loadAnnouncements();
    }


    Component.onCompleted:  {
        loadAnnouncements();
    }

    function loadAnnouncements() {
        // Load the list
        var m = announcementsList.model;
        m.modifyFilter("course_id=" + current_course_id);
        m.sortOn("posted_at");
        m.select();

    }



    ListView {
        id: announcementsList
        width: parent.width
        height: parent.height
        interactive: true
        focus: true
        spacing: 4
        highlightFollowsCurrentItem: false
        clip: true;

        ScrollBar.vertical: ScrollBar {}

        model: announcements_model

        highlight: Rectangle {
            width: announcementsList.width;
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
                height: 85
                implicitHeight: height
                Layout.fillHeight: true
                color: "lightgrey"
                radius: 3
                opacity: 0.5
                property int indexOfThisDelegate: index;

                RowLayout {
                    anchors.fill: parent

                    ColumnLayout
                    {
                        Layout.fillWidth: true
                        Layout.minimumWidth: 10
                        Layout.minimumHeight: 60

                        Text {
                            height: 30
                            verticalAlignment: Text.AlignVCenter
                            text: title
                            font.pointSize: 12
                        }
                        Text {
                            height: 15
                            verticalAlignment: Text.AlignVCenter
                            text: user_name
                            font.pointSize: 9
                        }
                        Text {
                            height: 30
                            text: message
                            font.pointSize: 11
                        }
                    }

                    Text {
                        height: 15
                        Layout.minimumHeight: 15
                        Layout.fillHeight: true
                        Layout.minimumWidth: 30
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignRight
                        text: posted_at
                        font.pointSize: 9
                    }
                    Text {
                        height: 15
                        Layout.minimumHeight: 15
                        Layout.minimumWidth: 32
                        text: "Att DL"
                        font.pointSize: 9
                    }


                }
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: { parent.color="lightsteelblue" }
                    onExited: { parent.color="lightgrey" }
                    onClicked: {
                        var item_url = App.getFieldValue(announcementsList.model, index, "url");
                        //global.current_page_url = item_url;
                        //pageClicked(item_url);
                    }
                }
            }
        }
    }


}

