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

Item {
    id: appCourseSelector
    anchors.fill: parent;

    property QtObject global;

    property string current_course_id: ""
    signal changed(string course_id);

    ComboBox {
        anchors.fill: parent
        id: selectedCourse
        model: courses_model
        textRole: "name";
        //color: "#032569";
        font.bold: true
        font.pointSize: 12
        flat: true;

        function fireChangeEvent() {
            console.log("fireChangeEvent");
            var course_id = App.getFieldValue(selectedCourse.model, selectedCourse.currentIndex, "id");
            global.current_course_id = course_id;
            appCourseSelector.changed(course_id);
        }

        delegate: ItemDelegate {
            width: selectedCourse.width;
            contentItem: Text {
                text: name;
                color: App.text_color;
                font: selectedCourse.font;
                elide: Text.ElideRight;
                verticalAlignment: Text.AlignVCenter
            }

            highlighted: selectedCourse.highlightedIndex === index;
        }

        onActivated: {
            console.log("Activated " + current_course_id);
            fireChangeEvent();

        }

        Component.onCompleted: {
            // Sort courses
            selectedCourse.model.sortOn("name");
            console.log("OnComplete - AppCourseSelector")
            //App.current_course = App.getFieldValue(this.model, selectedCourse.currentIndex, "id");
            //appCourseSelector.changed(App.current_course);
            fireChangeEvent();

        }


    }

}
