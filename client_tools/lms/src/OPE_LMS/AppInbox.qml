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

Page {
    id: page
    property QtObject global;
    property string current_course_id: "";

    signal conversationClicked(string item_id);

    property QtObject conversationsModel: conversations_model;
    property QtObject messagesModel: messages_model;

    padding: 3;

    Component.onCompleted:  {
        loadCanvasConversations();
    }

    function loadCanvasConversations() {
        // Load the list of conversations
        var m = conversationsModel;  // conversationsList.model;
        var curr_course = "course_" + current_course_id;
        console.log(curr_course);
        m.modifyFilter("context_code='" + curr_course + "'");
        //m.sortOn("title");
        m.sortOn("last_message_at", Qt.DescendingOrder);
        m.select();
        conversationsList.model = m;

        refreshMessagePane();

    }

    function refreshMessagePane() {
        // Reload the messages in the message pane based on the

        // current selected conversation
        if (readingPane.conversation_id == "-1") {
            console.log("Not refreshing messages - no conversation_id set");
            messagesList.model = undefined;
            return;
        }
        if (readingPane.conversation_id === readingPane.last_conversation_id) {
            console.log("Not refreshing messages - conversation_id hasn't changed");
            // Hasn't actually changed
            return;
        }


        // Load up a model and set its filter.
        console.log("Loading messages for conversation " + readingPane.conversation_id);
        var m = messagesModel;
        m.modifyFilter("conversation_id='" + readingPane.conversation_id + "'");
        m.sortOn("created_at", Qt.DescendingOrder);
        m.select();
        messagesList.model = m;
        readingPane.last_conversation_id = readingPane.conversation_id;
        //messagesList.forceLayout();

    }

    function saveReply(message_id, reply_text) {
        // Find the record for this message
        var record = App.findRecord(messagesModel, "id", message_id);
        if (record === undefined) {
            console.log("ERROR - saveReply - unable to pull message for " + message_id);
            return;
        }

        var conversation_id = App.getFieldValue(messagesModel, record.index, "conversation_id", "<ERROR>");
        var participating_user_ids = App.getFieldValue(messagesModel, record.index, "participating_user_ids", "<ERROR>");

        if (conversation_id === "<ERROR>" || participating_user_ids === "<ERROR>") {
            console.log("saveReply - ERROR - Unable to pull message info: " + message_id);
            return;
        }

        // Add a record with the new reply information
        var new_record = {};

        new_record["id"] = "<queued>";
        new_record["body"] = reply_text;
        new_record["author_id"] = "??";
        new_record["created_at"] = moment.utc().format();
        new_record["generated"] = "";
        new_record["forwarded_messages"] = "[]";
        new_record["attachments"] = "[]";
        new_record["media_comment"] = "";
        new_record["participating_user_ids"] = participating_user_ids;
        new_record["conversation_id"] = conversation_id;
        new_record["scope"] = "sent";
        new_record["is_active"] = "true";
        new_record["need_to_push"] = "true";

        var ret = messagesModel.newRecord(new_record);

        // Force message list to refresh
        readingPane.last_conversation_id = "-1";
        refreshMessagePane();

        return ret;
    }

    function get_possible_recipients() {
        // Get a list of recipients this user can send an email to.

        // NOTE - Right now it is instructors ONLY.
        var recipients = [];

        return recipients;
    }


    header: RowLayout {
        Text {
            id: header_text;
            text: "Inbox";
            font.bold: true;
            font.pixelSize: 26;
            padding: 6;
            color: App.text_color;
        }
        Rectangle {
            id: new_message;
            width: 24;
            //color: "red";
            height: 24;
            Layout.alignment: Qt.AlignVCenter | Qt.AlignRight;
            Layout.rightMargin: 16;
            radius: 4;

            ToolTip {
                id: ttNewMessage;
                text: "Start a new conversation";
                visible: false;
            }

            Image {
                source: "qrc:/images/new_message.png"
                anchors.fill: parent;
                fillMode: Image.PreserveAspectFit;
            }

            MouseArea {
                anchors.fill: parent;
                hoverEnabled: true;
                onEntered: {
                    new_message.color = App.highlight_color;
                    ttNewMessage.visible = true;
                }
                onExited: {
                    new_message.color = "#00000000";
                    ttNewMessage.visible = false;
                }
                onClicked: {
                    // Get the possible recipients for this course.
                    newMessagePopup.possible_recipients = get_possible_recipients();
                    // Show new message box
                    newMessagePopup.open();
                }
            }
        }
    }



    Item {
        id: conversationsPane
        x: 0
        y: 0
        width: 292
        //color: "#c01111"
        anchors.left: parent.left
        anchors.leftMargin: 4
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 4
        anchors.top: parent.top
        anchors.topMargin: 4


        ListView {
            id: conversationsList;
            anchors.fill: parent;
            anchors.margins: 4;
            interactive: true;
            focus: true;
            spacing: 3
            highlightFollowsCurrentItem: true;
            clip: true;

            ScrollBar.vertical: ScrollBar {}

            model: undefined;
            //model: conversations_model;

            highlight: Rectangle {
                width: conversationsList.width;
                height: 30;
                color: App.highlight_color;
                radius: 3;
                opacity: 0;
            }

            onCurrentItemChanged: {
                console.log("CurrentItemChanged: " + currentItem);

                // Let reading pane know subject changed
                if (currentItem) {
                    readingPane.selected_subject = conversationsList.currentItem.subject;
                    readingPane.conversation_id = conversationsList.currentItem.conversation_id;
                    readingPane.participants = conversationsList.currentItem.participants;
                    readingPane.context_name = conversationsList.currentItem.context_name;
                } else {
                    readingPane.conversation_id = "-1";
                    readingPane.selected_subject = "Select Conversation";
                }
            }

            delegate: Component {
                AppConversation {

                    onConversationClicked: {
                        console.log("Conversation Clicked: " + conversation_id);
                        // Set selected to this item
                        conversationsList.currentIndex = index;
                    }

                    conversation_id: App.getFieldValue(conversationsList.model, index, "id");
                    last_message_time: App.getFieldValue(conversationsList.model, index, "last_message_at");
                    last_message_text: App.getFieldValue(conversationsList.model, index, "last_message");
                    subject: App.getFieldValue(conversationsList.model, index, "subject");
                    message_count: App.getFieldValue(conversationsList.model, index, "message_count");
                    message_state: App.getFieldValue(conversationsList.model, index, "workflow_state");
                    participants: App.getFieldValue(conversationsList.model, index, "participants");
                    context_name: App.getFieldValue(conversationsList.model, index, "context_name")
                }
            }
        }
    }

    Item {
        id: readingPane
        //color: "#1459e1"
        anchors.right: parent.right
        anchors.rightMargin: 4
        anchors.left: parent.left
        anchors.leftMargin: 305
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 4
        anchors.top: parent.top
        anchors.topMargin: 4

        property string selected_subject: "Select Conversation";
        property string conversation_id: "-1";
        property string last_conversation_id: "-1";
        property string participants: "[]";
        property string context_name: "";

        onConversation_idChanged: {
            console.log("event onConversation_idChanged " + conversation_id)
            refreshMessagePane();

        }


        ListView {
            id: messagesList
            anchors.fill: parent;
            //height: readingPane.height;
            //width: parent.width;
            //y: rectangle.height;
            //Layout.minimumHeight: 60
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop
            //Layout.fillHeight: true;
            //Layout.fillWidth: true;

            interactive: true;
            focus: true;
            spacing: 3;
            highlightFollowsCurrentItem: true;
            clip: true;

            ScrollBar.vertical: ScrollBar {}

            header: Rectangle {
                id: headerPane;
                width: parent.width;
                color: App.bg_color;
                height: subject_text.paintedHeight + 16;
                visible: readingPane.conversation_id != "-1" ? true : false;

                Text {
                    id: subject_text;
                    //height: paintedHeight + 16;
                    width: parent.width;
                    // Subject
                    text: readingPane.selected_subject;
                    wrapMode: Text.WordWrap;
                    color: App.text_color;
                    font.bold: true;
                    font.pointSize: 18;
                    padding: 8;
                }
                Rectangle {
                    id: linebreak;
                    width: parent.width;
                    height: 3;
                    color: "#000000";
                    y: parent.height - 3;
                    //anchors.top: subject_text.bottom - 3;
                }
            }

            model: undefined; //messages_model;
            // Dummy model - will get replaced w real data at run-time
//            model: ListModel {
//                ListElement {
//                    conversation_id: "-1";
//                    message_id: "-1";
//                    participating_ids: "[1]";
//                    author_id: "-1";
//                    created_at: "July";
//                    body: "Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! Message text! ";
//                    scope: "Inbox";
//                    participant_data: "[]";
//                    context_name: "Intro to Algebra";

//                }
//            }

            delegate:
            AppMessage {

                /*onMessageClicked: {
                    console.log("Message Clicked: " + message_id);
                    // Set selected to this item
                    messagesList.currentIndex = index;
                }*/
                onReplyClicked: {
                    console.log("Reply Clicked: " + message_id);
                    replyPopup.message_id = message_id;
                    replyPopup.open();
                }

                conversation_id: App.getFieldValue(messagesList.model, index, "conversation_id");
                message_id: App.getFieldValue(messagesList.model, index, "id")
                participating_ids: App.getFieldValue(messagesList.model, index, "participating_ids");
                author_id: App.getFieldValue(messagesList.model, index, "author_id");
                created_at: App.getFieldValue(messagesList.model, index, "created_at");
                body: App.getFieldValue(messagesList.model, index, "body");
                scope: App.getFieldValue(messagesList.model, index, "scope");

                // Participants from conversation - needed because participating ids are just IDs
                participant_data: readingPane.participants;
                context_name: readingPane.context_name;


            }

        }

    }


    ReplyPopup {
        id: replyPopup
        parent: page // Overlay.overlay;

        onCancelClicked: {
            console.log("Reply - Cancel Clicked " + message_id);
            replyPopup.close();
        }

        onSendClicked: {
            console.log("Reply - Send Clicked " + message_id);
            saveReply(message_id, reply_text);
            replyPopup.close();

        }
    }

    NewMessagePopup {
        id: newMessagePopup
        parent: page;

        onCancelClicked: {
            console.log("New Message - cancel clicked ");
            newMessagePopup.close();
        }

        onSendClicked: {
            console.log("New Message - Send Clicked");
            saveNewMessage(message_text, recipient_id);
            newMessagePopup.close();
        }
    }


}












































/*##^## Designer {
    D{i:0;autoSize:true;height:480;width:640}D{i:3;anchors_height:422;anchors_width:320;anchors_x:308;anchors_y:3}
D{i:2;anchors_height:431;anchors_width:300;anchors_x:"-3";anchors_y:3}D{i:8;anchors_height:422;anchors_width:320;anchors_x:308;anchors_y:3}
}
 ##^##*/
