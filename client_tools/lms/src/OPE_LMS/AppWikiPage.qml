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

Page {
    property QtObject global;
    property string current_course_id: "";
    property string current_page_url: "";
    property bool is_loading: false;


    onCurrent_page_urlChanged: {
        console.log("AppWikiPage - current_page_url changed " + current_page_url);
        loadCanvasWikiPage();
    }
    onCurrent_course_idChanged: {
        console.log("AppWikiPage - current_course_id_changed " + current_course_id);
        loadCanvasWikiPage();
    }

    function loadCanvasWikiPage() {
        if (is_loading === true) {
            // Cancel load if we are already loading?
            console.log("Canceling load - already loading...");
            return;
        }

        is_loading = true;

        console.log("  - loadPage: " +  current_page_url);
        var m = pages_model
        m.modifyFilter("url='" + current_page_url + "' and course_id='" + current_course_id + "'");
        m.select();

        var page_body = "No Default Page Set";
        var page_title = "";
        for(var i = 0; i < m.rowCount(); i++) {
            page_body = App.getFieldValue(m, i, "body").toString("404 - Page Not Found");
            page_title = App.getFieldValue(m, i, "title").toString("");
        }

        // Add injected javascript to page
        console.log("Injecting ope webchannel...");
        page_body += "\n" + App.WebChannelJS;

        //console.log("Wiki Page Body: " + page_body);
        pageTitle.text = page_title;
        webView.loadHtml(page_body); //, "http://localhost:65525/");
    }

    Component.onCompleted: {
        console.log("AppWikiPage - onCompleted ");
        loadCanvasWikiPage();
    }

    header: Text {
        id: pageTitle
        text: "Page"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: App.text_color;
    }

    ColumnLayout {
        anchors.fill: parent;

        Rectangle {
            Layout.minimumHeight: 30
            Layout.minimumWidth: 30
            Layout.preferredHeight: 300
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            Layout.fillWidth: true
            //color: "red"

            WebView {
                anchors.fill: parent
                id: webView
                focus: true

                //loadProgress: 0

                onLoadingChanged: {
                    var err = loadRequest.errorString
                    var status = loadRequest.status
                    var url = loadRequest.url
                    if (status === WebView.LoadStartedStatus) {
                        console.log("AppWikiPage - Load Started " + url);
                    }
                    if (status === WebView.LoadFailedStatus) {
                        console.log("AppWikiPage - Load Failed " + url);
                        console.log(err);
                        is_loading = false;
                    }
                    if (status === WebView.LoadSucceededStatus) {
                        console.log("AppWikiPage - Load Succeeded " + url);
                        is_loading = true;
                    }
                    if (err) {
                        console.log("WView Error: " + err);
                    }

                }

            }
        }
    }




}
