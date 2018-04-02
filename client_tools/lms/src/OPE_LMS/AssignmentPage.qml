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
        loadAssignmentPage();
    }

    function loadAssignmentPage() {
        console.log("  - loadAssignmentPage: " +  App.current_page_url);
        var m = assignments_model
        m.modifyFilter("html_url='" + App.current_page_url + "'");
        m.select();

        var a_name = "ASSIGNMENT NAME";
        var a_desc = "ASSIGNMENT DESCRIPTION";
        for(var i = 0; i < m.rowCount(); i++) {
            a_name = App.getFieldValue(m, i, "name").toString();
            a_desc = App.getFieldValue(m, i, "description").toString();
            //page = App.getFieldValue(m, i, "body").toString("404 - Page Not Found");

        }

        //a_desc = "TEST DESC";
        descTest.text = a_desc;
        assignmentName.text = a_name;
        assignmentDescription.loadHtml(a_desc);

        // Webengine - need to write jscript to set the page
        //App.setHTML(webView, page);
        //webView.loadHtml(page);
    }

    Component.onCompleted: {

        loadAssignmentPage();


    }

    header: Text {
        id:headerText
        text: "Assignment"
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

    Drawer {
        id: turnInDrawer
        y: 0
        width: window.width * 1.0;
        height: window.height;
        edge: Qt.RightEdge;
        dragMargin: 0;
        closePolicy: Popup.NoAutoClose;

        Rectangle {
            color: "#ff0000"
            anchors.fill: parent;

            Text {
                text: "Drop assignment here"
            }
            DropArea {
                id: assignmentDrop
                anchors.fill: parent

                //keys: ["text/plain", ]
                onDropped: {

                    console.log("drop hastext " + drop.hasText + " - " + drop.text)
                    console.log("Drop action " + drop.proposedAction)
                    console.log(drop.urls)
                    console.log("Source "+ drop.source)
                    //console.log("Formats " + drop.formats)
                }
            }
        }
    }

    ColumnLayout {
        Text {
            id: assignmentName

        }
        Text {
            id: descTest

        }

        WebView {
            width: parent.width
            height: 60;
            Layout.fillHeight: true;
            id: assignmentDescription
            focus: true
            //loadProgress: 0

            onLoadingChanged: {
                var err = loadRequest.errorString
                var status = loadRequest.status
                console.log("Loading changed..." + status)
            }

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
