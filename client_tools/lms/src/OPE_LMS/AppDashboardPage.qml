import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material
import QtQuick.Controls.Universal
//import QtQuick.Controls.Styles
import QtQuick.Controls.Imagine
import QtQuick.Layouts 1.15

import QtQuick.Effects;

import QtWebView 1.1

import com.openprisoneducation.ope 1.0
import "App.js" as App

Page {
    property QtObject global;

    //signal pageClicked(string page_url);
    signal courseClicked(string course_id, string course_name, string course_code);

    padding: 3;

    property variant dashboard_colors: [
        "#BD3C14",
        "#FF2717",
        "#E71F63",
        "#8F3E97",
        "#65499D",
        "#4554A4",
        "#1770AB",
        "#0B9BE3",
        "#06A3B7",
        "#009688",
        "#009606",
        "#8D9900",
        "#8D9900",
        "#D97900",
        "#FD5D10",
        "#F06291"
    ];


    Component.onCompleted: {
        loadCanvasDashboard();
    }

    function loadCanvasDashboard() {
        // Load the list of courses
        var m = dashboardList.model;
        m.modifyFilter(""); //"course_id=" + current_course_id);
        m.sortOn("title");
        m.select();
    }

    header: Text {
        text: "Dashboard"
        font.bold: true;
        font.pixelSize: 26
        padding: 6
        color: App.text_color;
    }

    GridView {
        id: dashboardList
        width: parent.width
        height: parent.height
        interactive: true
        focus: true
        //spacing: 4
        highlightFollowsCurrentItem: false
        clip: true;
        //orientation: Qt.Horizontal
        cellWidth: 280
        cellHeight: 285


        ScrollBar.vertical: ScrollBar {}

        model: courses_model

        highlight: Rectangle {
            width: dashboardList.width;
            height: 30
            color: App.highlight_color;
            radius: 3
            opacity: 0
        }

        delegate: Component {
            Item {
                id: itemRoot;
                //anchors.fill: parent;
                width: 280;
                height: 285;
                property string item_color: dashboard_colors[Math.floor(Math.random()*dashboard_colors.length)];

                MultiEffect {
                    id: itemShadow
                    source: item;
                    anchors.fill: item;
                    //visible: false;
                    autoPaddingEnabled: true;
                    //paddingRect: Qt.rect(0, 0, parent.width, parent.height);
                    shadowEnabled: true;
                    shadowOpacity: 1.0;
                    shadowHorizontalOffset: 4;
                    shadowVerticalOffset: 4;
                    //shadowColor: Qt.rgba(0.0, 0.0, 0.0, 1.0);
                    shadowBlur: 1.0;
                    opacity: 0.5;
                    //visible: false;

                }

                Rectangle {
                    id: item
                    width: 263;
                    height: 267;
                    radius: 5
                    border.color: "grey";
                    border.width: 1;

                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter;
                        anchors.verticalCenter: parent.verticalCenter;
                        //Layout.fillWidth: true
                        width: 261
                        height: 265
                        implicitHeight: height
                        color: "#ffffff";
                        radius: 5
                        //opacity: 0.5
                        property int indexOfThisDelegate: index;


                        ColumnLayout {
                            anchors.fill: parent;
                            Layout.alignment: Qt.AlignTop;

                            Rectangle {
                                width: 261;
                                height: 145;
                                //Layout.width: width;
                                //Layout.height: height;
                                implicitHeight: 145;
                                implicitWidth: 261;
                                color: itemRoot.item_color;
                                radius: 0;
                                Layout.alignment: Qt.AlignTop;

                            }

                            Item {
                                id: course_text_area
                                //color: "blue";
                                height: 30;
                                width: parent.width
                                implicitWidth: parent.width;
                                implicitHeight: height;


                                //Layout.alignment: Qt.AlignTop;
                                Column {

                                    Text {
                                        id: item_name_text;
                                        //anchors.fill: parent;
                                        font.family: App.global_font_family;
                                        font.pixelSize: 14; //App.global_font_size;
                                        font.bold: true;
                                        textFormat: Text.StyledText;
                                        text: name;
                                        color: App.text_color;
                                        padding: 3;
                                        //renderType: Text.NativeRendering;
//                                        Accessible.name: item_name_text.text;
//                                        Accessible.description: item_name_text.text;
//                                        Accessible.role: Accessible.Button;


                                    }
                                    Text {
                                        id: item_course_text;
                                        //anchors.fill: parent;
                                        font.family: App.global_font_family;
                                        font.pixelSize: 16; //App.global_font_size;
                                        //font.bold: true;
                                        textFormat: Text.StyledText;
                                        text: course_code
                                        color: App.text_color;
                                        padding: 3;
                                        //renderType: Text.NativeRendering;
//                                        Accessible.name: item_course_text.text;
//                                        Accessible.description: item_course_text.text;
//                                        Accessible.role: Accessible.StaticText;
                                    }
                                }

                            }


                            Item {
                                height: 1;
                                width: parent.width;
                                Layout.fillHeight: true;
                            }
                        }

                    }
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true;
                        propagateComposedEvents: true;
                        onEntered: { itemShadow.opacity = 1.0; }
                        onExited: { itemShadow.opacity = 0.5; }
                        onClicked: (mouse)=> {
                            var item_url = App.getFieldValue(dashboardList.model, index, "url");
                            //global.current_page_url = item_url;
                            //pageClicked(item_url);
                            // Make click events propagate to other mousearea
                            mouse.accepted = false;
                        }


                        MouseArea {
                            // MOUSE AREA for course_text_area
                            // Making it a child of other mouse area lets it get sub area hover
                            //anchors.fill: course_text_area;
                            width: course_text_area.width;
                            height: course_text_area.height;
                            x: course_text_area.x;
                            y: course_text_area.y;
                            hoverEnabled: true;
                            //propagateComposedEvents: true;
                            cursorShape: Qt.PointingHandCursor
                            onEntered: {
                                //console.log("T1");
                                item_name_text.font.underline = true;
                                item_course_text.font.underline = true;
                                item_name_text.focus = true;
                            }
                            onExited: {
                                //console.log("T2");
                                item_name_text.font.underline = false;
                                item_course_text.font.underline = false;
                            }

                            onClicked: {
                                //console.log("T3");
                                // Show course
                                var course_name = App.getFieldValue(dashboardList.model, index, "name");
                                var course_code = App.getFieldValue(dashboardList.model, index, "course_code");
                                courseClicked(id, course_name, course_code);
                            }
                        }
                    }
                }
            }
        }
    }
}
