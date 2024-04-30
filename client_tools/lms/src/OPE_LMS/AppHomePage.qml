import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Universal 2.15
//import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.15
import QtQuick.Layouts 1.15

import QtWebView 1.1

import com.openprisoneducation.ope 1.0
import "App.js" as App

/*

  NOTE - This basically redirects to the other appropriate page based on
  the home page type

*/

Page {
    id: appHomePage;

    property QtObject global;

    property string current_course_id: "";
    property string current_page_url: "";
    property string current_assignment_id: "";

    onCurrent_course_idChanged: {
        loadHomePage();
    }

    padding: 3

    function loadHomePage() {
        // What kind of page is is?
        // - feed - Recent activity
        // - wiki - Wiki front page
        // - modules - show course modules
        // - assignments - show course assignments
        // - syllabus - show course syllabus
        var course_model = courses_model.copy();
        course_model.modifyFilter("id=" + current_course_id);
        course_model.select();
        var home_page_type = "wiki";
        for (var i = 0; i < course_model.rowCount(); i++) {
            home_page_type = App.getFieldValue(course_model, i, "default_view")
        }
        // Reset the filter
        course_model.destroy();
        console.log("home page default view " + home_page_type);

        switch(home_page_type) {
        case "feed":
            global.showFeedView();
            break;
        case "modules":
            global.showModulesView();
            break;
        case "assignments":
            global.showAssignmentsView();
            break;
        case "syllabus":
            global.showSyllabusView();
            break;
        case "wiki":
            findFrontPage();
            global.showWikiPageView();
            //homePageStack.replace(pageView);

            break;
        default:
            console.log("Unknown home_page_type " + home_page_type);
            findFrontPage();
            //homePageStack.replace(pageView);
            global.showWikiPageView();

            break;
        }

    }

    function findFrontPage() {

        console.log("  - findFrontPage: " + current_course_id);
        var m = pages_model.copy()
        m.modifyFilter("front_page=1 and course_id=" + current_course_id);
        m.select();

        var front_page_url = "";
        for(var i = 0; i < m.rowCount(); i++) {
            front_page_url = App.getFieldValue(m, i, "url").toString("");
            console.log("FRONT PAGE FOUND! " + current_page_url);
        }
        global.current_page_url = front_page_url;
        m.destroy();
    }

    Component.onCompleted: {
        loadHomePage();
    }

/*
    StackView {
        id: homePageStack
        initialItem: pageView
        anchors.fill: parent;
    }


    Component {
        id: pageView
        AppWikiPage {
            global: appHomePage.global;
            current_course_id: appHomePage.current_course_id;
            current_page_url: appHomePage.current_page_url;
        }
    }

    Component {
        id: modulesView
        AppModules {
            global: appHomePage.global;
            current_assignment_id: appHomePage.current_assignment_id
            current_course_id: appHomePage.current_course_id
            current_page_url: appHomePage.current_page_url
        }

    }
    */

}
