import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls.Universal 2.15
////import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.15
import QtQuick.Layouts 1.15

import QtWebView 1.1

//import com.openprisoneducation.ope 1.0
import "App.js" as App

Button {
    id: styledButton
    text: "Button";
    font.family: "Courier"
    Layout.fillHeight: false
    Layout.fillWidth: false
    Layout.preferredWidth: -1
    Layout.minimumWidth: 140
    //width: 40;
    property string text_color: App.text_color; // "#032569";
    property string text_down_color: App.text_color; //"#032569";
    spacing: 1
    display: AbstractButton.TextOnly
//    onClicked: {
//        styledButton.clicked();
//    }

    contentItem:
        Text {
            font.capitalization: Font.AllUppercase
            color: parent.down ? parent.text_color : parent.text_down_color;
            text: parent.text
            font.bold: true
            font.pointSize: 10
            //lineHeight: 0.8
            //font: parent.font
            opacity: enabled ? 1.0 : 0.3
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
}
