import QtQuick
import QtQuick.Layouts

Rectangle {
    property string question_id: "-1";
    property var answers: [];
    property string text: "";
    property string description: "";
    property string points: "";
    // MultipleChoice, TrueFalse, FillInBlank, FillInMultipleBlanks,
    // MultipleAnswers, MultipleDropDowns, Matching, NumericalAnswer,
    // FormulaQuestion, EsayQuestion, FileUpload, NoQuestion
    property string question_type: "TrueFalse";


    signal onSubmit();  // Call when user is saving/submitting the question
    signal onCancel();  // Call when cancel pushed

    // Setup the answers as needed
    function render_answers() {
        console.log("Render Answers");

        // Empty current children
        rowQAnswers.children.clear();

        for (var i=0; i < quizQuestion.answers.length; i++) {

        }

    }

    Component.onCompleted: render_answers();

    id: quizQuestion;
    anchors.fill: parent;
    Layout.fillWidth: true;
    color: "#ffffff";
    radius: 3;

    Layout.preferredHeight: 300;
    Layout.preferredWidth: 500;
    width: 500;
    height: 300;

    ColumnLayout {
        anchors.fill: parent;
        spacing: 0;

        Rectangle {
            color: "#bdbdbd";
            radius: 1
            border.width: 1
            Layout.alignment: Qt.AlignLeft | Qt.AlignTop;
            Layout.fillWidth: true;
            Layout.preferredWidth: parent.width;
            Layout.preferredHeight: 52;

            RowLayout {
                Layout.alignment: Qt.AlignTop;
                anchors.fill: parent

                Text {
                    id: txtQTitle
                    width: 300
                    height: 50
                    color: "#090e67"
                    text: quizQuestion.text;
                    font.pixelSize: 32
                    Layout.alignment: Qt.AlignLeft | Qt.AlignTop
                    font.bold: true
                    Layout.fillWidth: true
                    Layout.preferredHeight: 50
                    Layout.preferredWidth: 300
                    leftPadding: 5;
                }

                Text {
                    id: txtQPoints
                    text: quizQuestion.points;
                    font.pixelSize: 24
                    horizontalAlignment: Text.AlignRight
                    fontSizeMode: Text.FixedSize
                    Layout.alignment: Qt.AlignRight | Qt.AlignTop
                    Layout.preferredWidth: 80
                    Layout.preferredHeight: 50
                    rightPadding: 5;
                }
            }


        }


        Text {
            id: txtQDescription
            text: quizQuestion.description;
            font.pixelSize: 18;
            //Layout.fillHeight: true;
            Layout.fillWidth: true;
            leftPadding: 5;
            rightPadding: 5;
            padding: 5;

        }


        Rectangle {
            border.color: "#030303";
            border.width: 2
            Layout.preferredWidth: 300
            Layout.fillWidth: true;
            Layout.fillHeight: true;
            Layout.preferredHeight: 20;
            border: 2

            ColumnLayout {
                id: rowQAnswers
                //Layout.fillHeight: true;
                Layout.fillWidth: true;

                Loader { sourceComponent: qTrueAnswer }
                Loader { sourceComponent: qFalseAnswer }


            }



        }

    }


    Component {
        id: qTrueAnswer;

        Rectangle {
            color: "red"
            width: 300;
            height: 30;
        }
    }

    Component {
        id: qFalseAnswer;

        Rectangle {
            color: "blue";
            width: 300;
            height: 30;
        }
    }

}


