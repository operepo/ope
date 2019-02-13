import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.3
import QtQuick.Controls.Universal 2.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3

//import QtWebEngine 1.4
import QtWebView 1.1

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
        var assignment_id = "";
        for(var i = 0; i < m.rowCount(); i++) {
            a_name = App.getFieldValue(m, i, "name").toString();
            a_desc = App.getFieldValue(m, i, "description").toString();
            assignment_id = App.getFieldValue(m, i, "id").toString();
            //page = App.getFieldValue(m, i, "body").toString("404 - Page Not Found");

        }

        //a_desc = "TEST DESC";
        //descTest.text = a_desc;
        //assignmentName.text = a_name;
        headerText.text = "Assignment - " + a_name;        
        assignmentDescription.loadHtml(a_desc);

        // Load the assignment_submissions
        var m = assignment_submissions_model
        m.modifyFilter("assignment_id='" + assignment_id + "'");
        m.select();

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
        wrapMode: Text.Wrap;
    }

    contentData: Flickable {
        anchors.fill:  parent

        ScrollBar.vertical: ScrollBar {}


        ColumnLayout {
            anchors.fill: parent
            /*Text {
                width: parent.width
                height: 30
                id: assignmentName
                text: "ASSIGNMENT NAME"
                font.bold: true
                font.pixelSize: 18
                wrapMode: Text.Wrap


            }
            Text {
                id: descTest
                //width: parent.width
                Layout.fillWidth: true
                text: "DESC"

            }*/
            Rectangle {
                Layout.fillHeight: true;
                Layout.minimumHeight: 200
                Layout.fillWidth: true;
                Layout.minimumWidth: 50
                Layout.preferredWidth: parent.width
                WebView {
                    anchors.fill:  parent
                    //width: parent.width
                    //height: 60;

                    id: assignmentDescription
                    focus: true
                    //loadProgress: 0


                    onLoadingChanged: {
                        var err = loadRequest.errorString
                        var status = loadRequest.status
                        console.log("Loading changed..." + status)
                        if(status == WebView.LoadSucceededStatus) {
                            // Inject the webchannel stuff
                            console.log("Injecting webchannel js...");
                            assignmentDescription.runJavaScript(App.WebChannelJS,
                                                                function(result) {
                                                                    console.log(result);
                                                                });
                        } else if (status == WebView.LoadFailedStatus) {
                            console.log("Error loading page! " + err);
                        }
                    }

                }
            }


            Rectangle {
                //width: parent.width;
                //height: 90;
                //implicitHeight: height;
                //implicitWidth: width;
                Layout.minimumHeight: 60
                Layout.preferredHeight: 60
                Layout.maximumHeight: 60
                Layout.fillWidth: true
                Layout.minimumWidth: 50
                color: "lightgrey"
                clip: true
                // Location of submtted assignment
                ListView {
                    id: submittedAssignments
                    anchors.fill: parent
                    interactive: true
                    focus: false
                    spacing: 4
                    ScrollBar.vertical: ScrollBar {}

                    model: assignment_submissions_model

                    header: Component {
                        Text {
                            text: "Current Submissions"
                            font.bold: true
                            font.pointSize: 9
                        }
                    }

                    highlight: Rectangle {
                        width: submittedAssignments.width;
                        height: 15
                        color: "steelblue"
                        radius: 3
                        opacity: 0
                    }

                    delegate: Component {
                        Rectangle {
                            id: item
                            Layout.fillWidth: true;
                            width: parent.width;
                            height: 15;
                            implicitHeight: height;
                            color: "lightgrey"
                            radius: 3
                            opacity: 0.5
                            property int indexOfThisDelgate: index;

                            Row {
                                Text {
                                    height: 15
                                    verticalAlignment: Text.AlignVCenter;
                                    text: queued_on
                                    font.pixelSize: 8
                                }
                            }
                        }
                    }
                }
            }

            Rectangle {
                color: "lightsteelblue"
                border.color: "#dddddd"
                border.width: 1

                //width: parent.width
                //height: 72
                //implicitHeight: height
                //implicitWidth: parent.width
                Layout.minimumHeight: 60
                Layout.preferredHeight: 60
                Layout.maximumHeight: 60
                Layout.fillWidth: true;
                Layout.minimumWidth: 50


                Text {
                    text: "Drop Assignment Here!"
                    font.bold: true
                    font.pointSize: 20
                    anchors.fill: parent
                    verticalAlignment: Qt.AlignVCenter
                    horizontalAlignment: Qt.AlignHCenter
                }
                Image {
                    source: "/images/upload.png"
                    width: 60
                    height: 60
                }

                DropArea {
                    id: assignmentDrop
                    anchors.fill: parent

                    //keys: ["text/plain", ]
                    onDropped: {
                        // Pull current info for the assignment
                        var m = assignments_model
                        m.modifyFilter("html_url='" + App.current_page_url + "'");
                        m.select();

                        var course_id = "0";
                        var assignment_id = "0";

                        for(var i = 0; i < m.rowCount(); i++) {
                            assignment_id = App.getFieldValue(m, i, "id").toString();
                            course_id = App.getFieldValue(m, i, "course_id").toString();
                        }

                        console.log("drop hastext " + drop.hasText + " - " + drop.text)
                        console.log("Drop action " + drop.proposedAction)
                        console.log(drop.urls)
                        console.log("Source "+ drop.source)
                        //console.log("Formats " + drop.formats)

                        var txt_answer = ""; // Should be blank if dropping a file
                        var file_url = "";

                        if (drop.urls.length > 0) {
                            file_url = drop.urls[0];
                        }
                        console.log("-- Course id: " + course_id);
                        console.log("-- Assignemnt id: " + assignment_id);
                        var ret = mainWidget.canvas.queueAssignmentFile(course_id, assignment_id, txt_answer, file_url);
                        if (!ret) {
                            console.log("ERROR - Couldn't queue assignment file!");
                        }
                    }
                }
            }

        }

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

    footer: Button {
        text: "Debug Print"
        onClicked: {
            console.log("Calling debugPrint")
            mainWidget.debugPrint("");
        }
    }

}
