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
    property string current_quiz_id: "";
    property string current_course_id: "";

    signal quizClicked(string quiz_id);

    padding: 3


    Component.onCompleted:  {
        loadQuizzes();
    }

    function loadQuizzes() {
        // Load the list of quizzes
        var m = quizzesList.model;
        m.modifyFilter("quiz_id=" + current_quiz_id);
        m.sortOn("title");
        m.select();

    }

    header: Text {
        text: "Quizzes"
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

        model: quizzes_model

        highlight: Rectangle {
            width: quizzesList.width;
            height: 30
            color: App.highlight_color;
            radius: 3
            opacity: 0
        }

        delegate: Component {
            Rectangle {
                id: item
                Layout.fillWidth: true
                width: quizzesList.width
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
                        var item_id = App.getFieldValue(quizzesList.model, index, "id");
                        global.current_quiz_id = item_id;
                        quizClicked(item_id);
                    }
                }
            }
        }
    }
}
