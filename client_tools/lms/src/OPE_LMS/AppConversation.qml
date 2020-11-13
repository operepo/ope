import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Universal 2.15
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.15
import QtQuick.Layouts 1.15

import QtWebView 1.15

import com.openprisoneducation.ope 1.0
import "App.js" as App
import "moment-with-locales-2.26.0.js" as Moment

Item {
    id: element
    width: parent.width - 2;
    height: 120;
    clip: true;

    property string conversation_id: "0";
    property string last_message_time: "12:58pm";
    property string participants: "Smith, Bob (s777777), admin@ed, teacheraccount";
    property string subject: "Question for teacher!";
    property string last_message_text: "The answer to your question is 10 to the power of ten time 300.";
    property string message_count: "5";
    property string message_state: "unread";
    property string context_name: "";

    signal conversationClicked(string conversation_id);

    property string current_mail_image: "qrc:/images/mail.png";
    property bool is_hovered: false;
    property bool is_selected: element.ListView.isCurrentItem;

    onMessage_stateChanged: {
        current_mail_image = get_mail_image(message_state);
    }

    function get_mail_image(state) {
        if (state === "read") {
            return "qrc:/images/mail_open.png";
        } else if (state === "archived") {
            return "qrc:/images/box.png";
        } else { // unread
            return "qrc:/images/mail.png";
        }
    }


    Rectangle {
        id: rectangle
        color: is_hovered || is_selected ? App.highlight_color : App.bg_color;
        radius: 4
        border.width: 0
        anchors.fill: parent

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onEntered: { is_hovered=true; }
            onExited: { is_hovered=false; }
            onClicked: {
                conversationClicked(conversation_id);
            }
        }

    }


    ColumnLayout {
        id: columnLayout
        width: 39
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.left: parent.left
        anchors.leftMargin: 0

        Image {
            id: image
            x: 3
            y: 35
            width: 32
            height: 32
            sourceSize.height: 32
            sourceSize.width: 32
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            fillMode: Image.PreserveAspectFit
            source: current_mail_image;
        }
    }

    ColumnLayout {
        id: columnLayout1
        spacing: 0
        anchors.right: parent.right
        anchors.rightMargin: 40
        anchors.left: parent.left
        anchors.leftMargin: 39
        anchors.top: parent.top
        anchors.topMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0

        Label {
            id: txtLastMessageTime
            width: 200
            height: 21
            text: qsTr( moment(last_message_time).format('LLLL'));
            verticalAlignment: Text.AlignVCenter
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            topPadding: 0
            bottomPadding: 0
            font.pointSize: 10
            color: App.text_color;
            elide: "ElideRight";
        }

        Label {
            id: txtParticipants
            height: 30
            text: qsTr(App.format_participants(participants));
            wrapMode: Text.WordWrap
            verticalAlignment: Text.AlignVCenter
            bottomPadding: 0
            topPadding: 0
            horizontalAlignment: Text.AlignLeft
            font.pointSize: 12
            font.weight: Font.Bold
            font.bold: true
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            color: App.text_color;
            elide: "ElideRight";
        }

        Label {
            id: txtSubject
            width: 122
            text: qsTr(subject)
            font.italic: true
            verticalAlignment: Text.AlignVCenter
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            bottomPadding: 0
            topPadding: 0
            Layout.fillWidth: true
            font.pointSize: 11
            color: App.text_color;
            elide: "ElideRight";
        }

        Label {
            id: txtLastMessageText
            height: 32
            text: qsTr(last_message_text)
            wrapMode: Text.WordWrap
            verticalAlignment: Text.AlignVCenter
            Layout.fillWidth: true
            font.pointSize: 10;
            color: App.text_color;
            elide: "ElideRight";
            clip: true;
        }
    }

    ColumnLayout {
        id: columnLayout2
        x: 260
        width: 40
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0

        Rectangle {
            id: rectangle1
            x: 8
            y: 20
            width: 30
            height: 30
            color: "#4f4c4c"
            radius: 4
            border.color: "#00000000"
            Layout.minimumHeight: 30
            Layout.minimumWidth: 30
            Layout.preferredHeight: 30
            Layout.preferredWidth: 30
            Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
            Layout.fillWidth: false
            ToolTip {
                id: ttMessageCount
                text: "Messages in this conversation";
                visible: false;
            }
            MouseArea {
                anchors.fill: parent;
                hoverEnabled: true;
                onEntered: {
                    ttMessageCount.visible = true;
                }
                onExited: {
                    ttMessageCount.visible = false;
                }
            }

            Label {
                id: txtMessageCount
                width: 30
                height: 30
                text: qsTr(message_count)
                verticalAlignment: Text.AlignVCenter
                lineHeight: 1
                rightPadding: 0
                font.weight: Font.Bold
                horizontalAlignment: Text.AlignHCenter
                leftPadding: 0
                padding: 0
                bottomPadding: 0
                topPadding: 0
                font.bold: true
                font.pointSize: 8
                color: "white";
            }
        }
    }



}













































/*##^## Designer {
    D{i:1;anchors_height:120;anchors_width:300}D{i:2;anchors_height:100;anchors_width:100;anchors_x:235;anchors_y:156}
D{i:5;anchors_height:480;anchors_width:535;anchors_x:39;anchors_y:0}D{i:4;anchors_height:480;anchors_width:39;anchors_x:0;anchors_y:0}
D{i:10;anchors_height:480;anchors_width:60;anchors_x:580;anchors_y:0}D{i:9;anchors_height:480;anchors_width:535;anchors_x:39;anchors_y:0}
}
 ##^##*/
