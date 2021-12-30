import QtQuick 2.0

Rectangle {
    id: quizquestion;
    anchors.fill: parent;
    color: "#ffffff";

    Row {
        id: qqMainRow
        anchors.fill: parent;

        Column {
            id: qqHeaderColumn;
            anchors.left: parent.left
            anchors.right: parent.right

            Text {
                id: txtQTitle
                text: qsTr("Question Title")
                font.pixelSize: 12
            }

            Text {
                id: txtQPoints
                text: qsTr("Question Points")
                font.pixelSize: 12
            }
        }

        Text {
            id: txtQDescription
            text: qsTr("Text")
            font.pixelSize: 12
        }

        QQ_TrueFalseAnswer {}

        QQ_TrueFalseAnswer {}


        Repeater {
            id: rowQAnswers
            anchors.left: parent.left
            anchors.right: parent.right

        }
    }

}
