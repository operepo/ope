import QtQuick 2.10
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.2
import QtQuick.Controls.Universal 2.2
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    property string current_course_id: "";
    property string current_page_url: "";

    padding: 3

    onCurrent_course_idChanged: {
        console.log("...Course id changed to: " + current_course_id);
        loadHomePage();
    }

    function loadHomePage() {
        // What kind of page is is?
        // - feed - Recent activity
        // - wiki - Wiki front page
        // - modules - show course modules
        // - assignments - show course assignments
        // - syllabus - show course syllabus
        var course_model = courses_model.copy();
        course_model.modifyFilter("course_id=" + current_course_id);
        course_model.select();
        var home_page_type = "wiki";
        for (var i = 0; i < course_model.rowCount(); i++) {
            home_page_type = App.getFieldValue(course_model, i, "")
        }
        // Reset the filter
        course_model.destroy();


        console.log("  - loadHomePage: " + current_course_id);
        var m = pages_model
        m.modifyFilter("front_page=1 and course_id=" + current_course_id);
        m.select();

        var page = "No Default Page Set";
        var page_url = "";
        for(var i = 0; i < m.rowCount(); i++) {
            page = App.getFieldValue(m, i, "body").toString("No Default Page Set");
            page_url = App.getFieldValue(m, i, "html_url").toString("");
            //page = App. m.data(m.index(i, m.getColumnIndex("body")), Qt.DisplayRole).toString("Default");
            //page = m.getRecord(i)["body"].toString("Default String");
        }

        current_page_url = page_url;
        //App.setHTML(webView, page);
        webView.loadHtml(page);
    }

    Component.onCompleted: {
        loadHomePage();
    }


    StackView {
        id: homePageStackView
        initialItem: homePage
    }


    Component {
        id: pageView


    }

}
