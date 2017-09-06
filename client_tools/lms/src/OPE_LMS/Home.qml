import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.2
import QtQuick.Layouts 1.0
//import QtWebView 1.1
import QtWebEngine 1.4

import com.openprisoneducation.ope 1.0

Item {
    function setHTML(wView, html) {
        // Use JS to write out the HTML to the web engine
        // Stupid hack because QT didn't provide this

        var js = "document.body.innerHTML='" + html.replace("'", "\'") + "'";
        wView.runJavaScript(js, function(result) {console.log(result); });
    }

    Text {
        text: "Home Screen"
    }
    Component.onCompleted: {
        var m = pages_model
        m.modifyFilter("front_page=1")

        var page = "";
        for(var i = 0; i < m.rowCount(); i++) {
            page = m.data(m.index(i, m.getColumnIndex("body")), Qt.DisplayRole).toString("Default");
            //page = m.getRecord(i)["body"].toString("Default String");
        }

        setHTML(webView, page);
    }


    WebEngineView {
        width: 200
        height: 200
        id: webView
        focus: true


    }


}
