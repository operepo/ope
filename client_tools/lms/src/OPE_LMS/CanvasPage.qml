import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.2
import QtQuick.Layouts 1.0
import QtWebView 1.1
//import QtWebEngine 1.4

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    signal refreshPage();
    signal loadPage(string page_url, string page_type);

    onRefreshPage: {
        console.log("RefreshPageCalled");
        loadCanvasPage();
    }

    function loadCanvasPage() {
        console.log("  - loadPage: " +  App.current_page_url);
        var m = pages_model
        m.modifyFilter("url='" + App.current_page_url + "'");
        m.select();

        var page = "No Default Page Set";
        for(var i = 0; i < m.rowCount(); i++) {
            page = App.getFieldValue(m, i, "body").toString("404 - Page Not Found");
        }

        // Webengine - need to write jscript to set the page
        //App.setHTML(webView, page);
        //webView.url = "https://localhost";
        webView.loadHtml(page);
        //webView.url = "https://canvas.correctionsed.com/login"
        //webView.url = "https://google.com"
    }

    Component.onCompleted: {

        loadCanvasPage();


    }

    header: Text {
        text: "Page"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
    }

    /*
    WebEngineView {
        anchors.fill: parent
        id: webView
        focus: true

        onCertificateError: {
            console.log("Ignoring cert error - webengine")
            error.ignoreCertificateError();
        }


    }
    */


    WebView {
        anchors.fill: parent
        id: webView
        focus: true
        //loadProgress: 0

        onLoadingChanged: {
            var err = loadRequest.errorString
            var status = loadRequest.status
            console.log("Loading changed..." + status)
        }



    }

    footer: Button {
        text: "Debug Print"
        onClicked: {
            console.log("Calling debugPrint")
            mainWidget.debugPrint("");
        }
    }

}
