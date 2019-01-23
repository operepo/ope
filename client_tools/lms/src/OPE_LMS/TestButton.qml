import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.3
import QtQuick.Controls.Universal 2.3
import QtQuick.Controls.Styles 1.4
import QtQuick.Controls.Imagine 2.3
import QtQuick.Layouts 1.3

import com.openprisoneducation.ope 1.0

Rectangle {
    color: "#e13131"
    Text {
        text: "Hi"
    }

    MouseArea {
        anchors.fill: parent;

        onClicked: {
            console.log("Clicked");
            mainWidget.debugPrint("Debug print");

        }
    }

}
