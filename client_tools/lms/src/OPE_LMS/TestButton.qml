import QtQuick 2.0

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
