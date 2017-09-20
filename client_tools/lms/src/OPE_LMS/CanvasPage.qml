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
    signal refreshPage();

    onRefreshPage: {
        console.log("RefreshPageCalled");
        loadHomePage();
    }

    function loadPage() {
        console.log("  - loadPage: " +  App.current_page_url);
        var m = pages_model
        m.modifyFilter("url='" + App.current_page_url + "'");
        m.select();

        var page = "No Default Page Set";
        for(var i = 0; i < m.rowCount(); i++) {
            page = App.getFieldValue(m, i, "body").toString("404 - Page Not Found");
        }

        App.setHTML(webView, page);
    }

    Component.onCompleted: {
        loadPage();


    }

    header: Text {
        text: "Page"
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
