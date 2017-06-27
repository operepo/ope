import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4

ApplicationWindow {
    visible: true
    id: window
    objectName: "window"
    width: 900
    height: 600
    title: qsTr("OPE - Learning Resource System")
        

    Component.onCompleted: {
        // if first run, open up the first run drawer
        if (mainWidget.isAppCredentialed() === false) {
            syncDrawer.open();
            //firstRunDrawer.open();
        }
    }

    Connections {
        target: mainWidget
        onShowCanvasLogin:
        {
            //console.log("Change url: " + url);
            loginWebView.url = url;           
        }
    }

    header: ToolBar
    {
        RowLayout {
            anchors.fill: parent;
            ToolButton {
                text: qsTr("Login")
                onClicked: loginDrawer.open();
            }
            ToolButton {
                text: qsTr("Sync")
                onClicked: syncDrawer.open();
            }
            ToolButton {
                text: qsTr("Resources");
                onClicked: resourcesDrawer.open();
            }
        }

    }

    Drawer {
        id: firstRunDrawer
        y: 0
        width: window.width * 1.0;
        height: window.height;
        edge: Qt.RightEdge;
        dragMargin: 0;
        closePolicy: Popup.NoAutoClose;

        ColumnLayout {
            Label {
                text: "Student Setup";
                font.pixelSize: 24;
                font.bold: true;
                color: "darkblue"

            }
        }
    }

    Drawer
    {
        id: loginDrawer
        y: 0; //header.height
        width: window.width * 1.0
        height: window.height; //window.height - header.height
        edge: Qt.LeftEdge
        dragMargin: 0

        ColumnLayout
        {
            Label {
                text: "Login To Canvas"
                font.bold: true;
                font.pixelSize: 24;
                color: "darkblue";
            }
            GridLayout
            {
                columns: 2

                Label { text: "User Name:"; }
                TextField {
                    id: user_name;
                    placeholderText: qsTr("Enter User Name")
                }

                Label { text: "Password:"; }
                TextField {
                    id: password
                    placeholderText: qsTr("Enter Password")
                    passwordCharacter: "*"
                    echoMode: TextInput.Password
                }

                Button {
                    text: "Login"
                    onClicked: {
                        //var ret = database.auth_student(user_name.text, password.text);
                        var ret = mainWidget.canvasAuthenticateUser(user_name.text, password.text);
                        if (ret === true) {
                            // Login succeeded
                            loginMessage.text = "Found local account - welcome";
                        } else {
                            // Login failed
                            loginMessage.text = "Invalid username or password!";
                        }
                    }
                }
                Button {
                    text: "Cancel"
                    onClicked: loginDrawer.close();
                }
            }
            Label {
                id: loginMessage
                text: ""
                color: "#ff0000"

            }
            Label {
                text: loginWebView.url
            }
            Label {
                text: loginWebView.title
            }

            Rectangle
            {
                color: "darkblue"
                width: 600
                height: 300

                WebEngineView {
                   anchors.fill: parent
                   id: loginWebView
                   objectName: "loginWebView"
                   width: 800
                   height: 300
                   //url: 'https://canvas.correctionsed.com/login/oauth2/auth?client_id=10000000000004&redirect_uri=http://localhost:1337/cb&response_type=code&scope&state=GlzDhlij'
                   //url: "https://canvas.correctionsed.com/login";

                   //Component.onCompleted: { loginWebView.loadHtml("HELLO"); }
                   Component.onCompleted: {
                       //mainWidget.setupLoginWebView(loginWebView);
                   }

                   onCertificateError:
                   {
                       // Allow test certs
                       //console.log("Ignore ssl error?");
                       error.ignoreCertificateError();
                       return true;
                   }

                   onLoadingChanged: {
                       console.log("Loading changed..." + loadRequest.url);
                       console.log("Status: " + loadRequest.status + " -- Start: " +
                                   WebEngineView.LoadStartedStatus + ", Stopped: " + WebEngineView.LoadStoppedStatus +
                                   ", Success: " + WebEngineView.LoadSucceededStatus + ", Failed: " + WebEngineView.LoadFailedStatus);
                       if (loadRequest.errorString)
                           console.error("Error String: " + loadRequest.errorString);
                       console.log(loginWebView.Page);
                       if (loadRequest.status === WebEngineLoadRequest.LoadSuccessStatus) {
                           if (loadRequest.url.indexOf("localhost:1337/cb?code=") !== -1) {
                               // Confirm?
                               console.log("Confirm login");
                           }
                       }
                   }

               }
            }


        }

    }

    Drawer
    {
        id: resourcesDrawer
        y: header.height
        width: window.width * 0.4
        height: window.height - header.height
        edge: Qt.RightEdge
        dragMargin: 0

        ColumnLayout {
            Label {
                id: resources_title
                text: "Resources"
            }


            ListView {
                width: parent.width
                height: parent.height - resources_title.height
                model: resources_model

                highlight: Rectangle { color: "lightsteelblue"; radius: 5; }

                delegate: Text {
                    text: resource_name

                }
            }
        }

    }

    Drawer
    {
        id: syncDrawer
        y: header.height
        width: window.width * 0.6
        height: window.height - header.height
        edge: Qt.RightEdge
        dragMargin: 0

        ColumnLayout
        {
            Label { text: "Sync..."; }

            WebEngineView {
               anchors.fill: parent
               id: syncWebView
               objectName: "syncWebView"
               width: 800
               height: 300
               //url: 'https://canvas.correctionsed.com/login/oauth2/auth?client_id=10000000000004&redirect_uri=http://localhost:1337/cb&response_type=code&scope&state=GlzDhlij'
               //url: "https://canvas.correctionsed.com/login";

               onCertificateError:
               {
                   // Allow test certs
                   error.ignoreCertificateError();
                   return true;
               }

               onLoadingChanged: {
                   console.log("Loading changed..." + loadRequest.url);
                   console.log("Status: " + loadRequest.status + " -- Start: " +
                               WebEngineView.LoadStartedStatus + ", Stopped: " + WebEngineView.LoadStoppedStatus +
                               ", Success: " + WebEngineView.LoadSucceededStatus + ", Failed: " + WebEngineView.LoadFailedStatus);
                   if (loadRequest.errorString)
                       console.error("Error String: " + loadRequest.errorString);
                   if (loadRequest.status === WebEngineLoadRequest.LoadSuccessStatus) {
                       if (loadRequest.url.indexOf("localhost:1337/cb?code=") !== -1) {
                           // Confirm?
                           console.log("Confirm login");
                       }
                   }
               }
            }
        }

    }

    SwipeView {
        id: swipeView
        anchors.fill: parent
        currentIndex: tabBar.currentIndex

        Page {

        }

        Page {
            Label {
                text: qsTr("Second page")
                anchors.centerIn: parent
            }
        }
//        Page {
//            WebView {
//                id: webView;
//                objectName: "testWebView"
//                anchors.fill: parent;
//                url: "http://localhost:8080";

//            }
//        }
    }

    footer: TabBar {
        id: tabBar
        currentIndex: swipeView.currentIndex
        TabButton {
            text: qsTr("First")
        }
        TabButton {
            text: qsTr("Second")
        }
        TabButton {
            text: qsTr("WebView")
        }
    }
}
