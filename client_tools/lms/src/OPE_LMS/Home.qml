import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.2
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    property string current_course_id: App.current_course;
    signal refreshPage();

    onRefreshPage: {
        console.log("RefreshPageCalled");
        loadHomePage();
    }

    onCurrent_course_idChanged: {
        console.log("Course id changed to: " + current_course_id);
        loadHomePage();
    }



    function loadHomePage() {
        console.log("  - loadHomePage: " + current_course_id + "  " + App.current_course);
        var m = pages_model
        m.modifyFilter("front_page=1 and course_id=" + App.current_course);
        m.select();

        var page = "No Default Page Set";
        for(var i = 0; i < m.rowCount(); i++) {
            page = App.getFieldValue(m, i, "body").toString("No Default Page Set");
            //page = App. m.data(m.index(i, m.getColumnIndex("body")), Qt.DisplayRole).toString("Default");
            //page = m.getRecord(i)["body"].toString("Default String");
        }

        App.setHTML(webView, page);
    }

    Component.onCompleted: {
        loadHomePage();


    }

    header: Text {
        text: "Home Screen"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
    }

    WebEngineView {
        anchors.fill: parent
        id: webView
        focus: true


    }


}
