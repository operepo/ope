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
import "moment-with-locales-2.26.0.js" as Moment

Item {
    id: element;
    width: parent.width;
    //height: 160;
    height: rootPane.height;


    property string conversation_id: "0";
    property string message_id: "0";
    property string participating_ids: "[]";
    property string author_id: "0";
    property string created_at: "Jun 1, 2020";
    property string body: "MESSAGE BODY";
    property string scope: "";

    // Participants from conversation - needed because participating ids are just IDs
    property string participant_data: "";
    property string context_name: "Intro to algebra";


    signal messageClicked(string message_id);
    signal replyClicked(string message_id);

    property string message_participants: "Smith, Bob (s777777), Instructor1"
    property string current_mail_image: "qrc:/images/mail.png";
    property bool is_hovered: false;
    property bool is_reply_hovered: false;
    property bool is_selected: element.ListView.isCurrentItem;


    onParticipant_dataChanged: {
        // Recalculate the participant information
        message_participants = App.format_participants(participant_data);
    }

    Rectangle {
        id: rootPane;
        //color: App.bg_color;
        radius: 4;
        x: 3;
        y: 3;
        width: parent.width - 8;
        height: messageColumn.height;
        anchors.margins: 3;

        MouseArea {
            anchors.fill: parent;
            hoverEnabled: true;
            onEntered: { is_hovered=true; }
            onExited: { is_hovered=false; }
            onClicked: {
                messageClicked(message_id);
            }
        }


        Column {
            id: messageColumn;
            spacing: 0;
            width: parent.width;

            Item {
                id: messageTopRow;
                width: parent.width;
                height: 60

                Rectangle {
                    x: 0;
                    y: 0;
                    id: avatarPane;
                    width: 60;
                    height: 60
                    Image {
                        anchors.fill: parent;
                        verticalAlignment: Image.AlignVCenter;
                        horizontalAlignment: Image.AlignHCenter;
                        width:48;
                        fillMode: Image.PreserveAspectFit;
                        source: "qrc:/images/default_avatar.png";
                    }

                }
                Rectangle {
                    id: topMiddlePane;
                    height: 60
                    //color: "#539e5e"
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 61
                    anchors.right: parent.right
                    anchors.rightMargin: 150

                    Column {
                        anchors.fill: parent;

                        Label {
                            id: txtLastMessageTime;
                            width: parent.width;
                            height: 15;
                            padding: 3;
                            text: qsTr( moment(created_at).format('LLLL') );
//                            anchors.right: parent.right
//                            anchors.rightMargin: 8
//                            anchors.top: parent.top
//                            anchors.topMargin: 8
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignTop;
                            topPadding: 0;
                            bottomPadding: 0;
                            font.pointSize: 10;
                            color: App.text_color;
                            elide: "ElideRight";
                        }

                        Label {
                            id: txtParticipants;
                            height: 30;
                            y: 15;
                            width: parent.width;
                            text: qsTr(message_participants);
                            padding: 3;
                            wrapMode: Text.WordWrap;
                            verticalAlignment: Text.AlignVCenter;
                            bottomPadding: 0;
                            topPadding: 0;
                            horizontalAlignment: Text.AlignLeft;
                            font.pointSize: 12;
                            font.weight: Font.Bold;
                            font.bold: true;
                            Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
                            color: App.text_color;
                            elide: "ElideRight";
                        }
                        Label {
                            id: txtCourse;
                            y: 45;
                            width: parent.width;
                            height: 15;
                            text: qsTr(context_name);
                            padding: 3;
                            wrapMode: Text.WordWrap;
                            verticalAlignment: Text.AlignTop;
                            bottomPadding: 0;
                            topPadding: 0;
                            horizontalAlignment: Text.AlignLeft;
                            font.pointSize: 10;
                            font.weight: Font.Light;
                            font.bold: false;
                            Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
                            color: App.text_color;
                            elide: "ElideRight";
                        }
                    }


                }

                Rectangle {
                    id: topRightPane;
                    x: 204
                    width: 60
                    height: 60
                    //color: "#45714c"
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.top: parent.top
                    anchors.topMargin: 0
                    Image {
                        verticalAlignment: Image.AlignVCenter;
                        horizontalAlignment: Image.AlignHCenter;
                        height: 25;
                        fillMode: Image.PreserveAspectFit;
                        source: "qrc:/images/upload_file.png";
                        visible: message_id === "<queued>" ? true : false;

                        ToolTip {
                            id: queuedToolTip;
                            text: "Message queued to sync";
                            visible: false;
                        }

                    }

                    Image {
                        id: replyImage;
                        verticalAlignment: Image.AlignVCenter;
                        horizontalAlignment: Image.AlignHCenter;
                        height: 25;
                        fillMode: Image.PreserveAspectFit;
                        source: "qrc:/images/reply.png";
                        visible: message_id === "<queued>" ? false : true;
                        Rectangle {
                            anchors.fill: parent;
                            id: replyHighlight;
                            radius: 4;
                            color: is_reply_hovered ? App.highlight_color2 : App.bg_color2;
                            z: -1;
                        }
                        ToolTip {
                            id: replyToolTip;
                            text: "Reply to this conversation";
                            visible: false;
                        }

                    }
                    MouseArea {
                        id: replyMouseArea
                        anchors.fill: parent;
                        hoverEnabled: true;
                        onEntered: {
                            is_reply_hovered=true;
                            if (replyImage.visible) {
                                replyToolTip.visible = true;
                            } else {
                                queuedToolTip.visible = true;
                            }
                        }
                        onExited: {
                            is_reply_hovered=false;
                            if (replyImage.visible) {
                                replyToolTip.visible = false;
                            } else {
                                queuedToolTip.visible = false;
                            }
                        }

                        onClicked: {
                            // Signal that the reply button was clicked so we
                            // can show the popup
                            if (message_id !== "<queued>") {
                                // Don't allow replies to queued messages
                                replyClicked(message_id);
                            }
                        }

                    }
                }
            }

            Rectangle {
                id: bodyTextPane
                height: txtBodyText.paintedHeight + 16;
                width: parent.width;

                Label {
                    id: txtBodyText;
                    x: 8
                    y: 8
                    text: qsTr(body);
                    font.pointSize: 11;
                    width: parent.width;
                    //anchors.fill: parent;
                    padding: 3;
                    wrapMode: Text.WrapAtWordBoundaryOrAnywhere;
                    color: App.text_color;
                    //height: txtBodyText.paintedHeight;

                }
            }

            Rectangle {
                id: linebreak;
                y: 0;
                width: parent.width;
                height: 3;
                color: "#000000";
            }

        }

    }


//    ColumnLayout {
//        id: columnLayout3;
//        spacing: 4;
//        width: parent.width;
//        //height: bodyPane.height + rectangle3.height;


//        Row {
//            id: rowLayout;
//            width: parent.width;
//            height: rectangle3.height;

//            Item {
//                id: rectangle2;
//                x: 0;
//                width: 50;
//                height: 60;

//            }

//            Item {
//                id: rectangle3;
//                x: 49;
//                width: 400;
//                height: 60;


//                Label {
//                    id: txtParticipants;
//                    height: 40;
//                    width: parent.width;
//                    text: qsTr(message_participants);
//                    padding: 3;
//                    wrapMode: Text.WordWrap;
//                    verticalAlignment: Text.AlignTop;
//                    bottomPadding: 0;
//                    topPadding: 0;
//                    horizontalAlignment: Text.AlignLeft;
//                    font.pointSize: 12;
//                    font.weight: Font.Bold;
//                    font.bold: true;
//                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
//                    color: App.text_color;
//                    elide: "ElideRight";
//                }
//                Label {
//                    id: txtCourse;
//                    y: 40;
//                    width: parent.width;
//                    height: 20;
//                    text: qsTr(context_name);
//                    padding: 3;
//                    wrapMode: Text.WordWrap;
//                    verticalAlignment: Text.AlignTop;
//                    bottomPadding: 0;
//                    topPadding: 0;
//                    horizontalAlignment: Text.AlignLeft;
//                    font.pointSize: 10;
//                    font.weight: Font.Light;
//                    font.bold: false;
//                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
//                    color: App.text_color;
//                    elide: "ElideRight";
//                }
//            }

//            Item {
//                id: rectangle4;
//                x: 448;
//                y: 0;
//                width: parent.width;
//                height: 60;

//                Label {
//                    id: txtLastMessageTime;
//                    width: parent.width;
//                    height: 30;
//                    text: qsTr(created_at);
//                    padding: 3;
//                    verticalAlignment: Text.AlignVCenter;
//                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
//                    topPadding: 0;
//                    bottomPadding: 0;
//                    font.pointSize: 10;
//                    color: App.text_color;
//                    elide: "ElideRight";
//                }
//            }
//        }

//        Item {
//            id: bodyPane;
//            width: parent.width;
//            height: txtBodyText.height;
//            //color: "green";

//            Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom;

//            Label {
//                id: txtBodyText;
//                text: qsTr(body);
//                font.pointSize: 11;
//                anchors.fill: parent;
//                padding: 3;
//                wrapMode: Text.WordWrap;
//                color: App.text_color;
//                height: txtBodyText.paintedHeight;

//            }
//        }
//    }

}























/*##^## Designer {
    D{i:8;anchors_y:8}D{i:7;anchors_width:150;anchors_x:204}D{i:6;anchors_width:143;anchors_x:61;anchors_y:0}
}
 ##^##*/
