import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: root;
    property string question_id: "-1";
    property string answer_id: "-1";
    property string answer_text: "True";
    property string answer_comment: "";
    property bool checked: false;

    signal changed(); // Fired when checked changes

    color: "#ffffff";
    Layout.fillHeight: true;
    Layout.fillWidth: true;
    Layout.minimumHeight: 40;
    Layout.minimumWidth: 500;
    border: 1;

    RowLayout {
        anchors.fill: parent;
        Layout.alignment: Qt.AlignLeft | Qt.AlignTop;

        Accessible.name: root.answer_text;
        Accessible.description: "";

        CheckBox {
            id: answerChecked;
            text: "";
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
            Accessible.ignored: true;
            Layout.fillHeight: true;
        }

        Text {
            id: answerText;
            Layout.fillWidth: true;
            Layout.fillHeight: true;
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
            text: "TF Answer";

            Accessible.ignored: true;
        }


    }



}



/*##^##
Designer {
    D{i:0;autoSize:true;height:40;width:500}D{i:2}D{i:3}D{i:1}
}
##^##*/
