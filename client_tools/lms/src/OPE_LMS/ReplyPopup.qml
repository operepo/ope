import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Universal 2.15
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.15
import QtQuick.Layouts 1.15

import QtWebView 1.1

//import com.openprisoneducation.ope 1.0
import "App.js" as App


Popup {
    id: replyPopup
    contentWidth: 400;
    contentHeight: 300;

    property string message_id: "-1";


    signal sendClicked(string message_id, string reply_text);
    signal cancelClicked();
    width: 500;
    height: 300;
    modal: true;

    // Position in the middle of the window?

    clip: true;
    focus: true;

    onMessage_idChanged: {
        // Clear the form
        replyBody.text = "";
    }

    onVisibleChanged: {
        console.log("visible changed...");
        replyBody.focus = true;
        replyBody.forceActiveFocus();
    }

    enter: Transition {
              NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 2.0; }
          }
    exit: Transition {
              NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 2.0; }
          }

    background: Rectangle {
        anchors.fill: parent;
        color: App.bg_color;
        z: -1;
    }


    ColumnLayout {
        anchors.fill: parent;

        Text {
            text: "Reply";
            font.bold: true;
            font.pixelSize: 26;
            padding: 6;
            color: App.text_color;

        }

        ScrollView {
            Layout.fillHeight: true;
            Layout.fillWidth: true;
            clip: true;

            TextArea {
                id: replyBody
                clip: true;
                text: "";
                focus: true;

                placeholderText: "[Enter Message Here]";

            }
        }

        RowLayout {
            Layout.preferredWidth: parent.width;
            Layout.fillWidth: false

            StyledButton {

                id: cancelReply
                text: "Cancel"
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                onClicked: {
                    cancelClicked();
                }
            }

            StyledButton {
                id: saveReply
                text: "Send"
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

                onClicked: {
                    sendClicked(replyPopup.message_id, replyBody.text);
                }
            }
        }
    }
}

