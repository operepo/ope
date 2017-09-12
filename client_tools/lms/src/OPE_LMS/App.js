.pragma library

var current_course = "";
var current_course_name = "";
var current_page_url = "";


function getFieldValue(model, row, field_name) {
    var ret = undefined;
    var i =  model.getColumnIndex(field_name);
    var index = model.index(row, i);
    ret = model.data(index, Qt.DisplayRole);
    return ret;
}

function setHTML(wView, html) {
    // Use JS to write out the HTML to the web engine
    // Stupid hack because QT didn't provide this

    var js = "document.body.innerHTML='" + html.replace("'", "\'") + "'";
    wView.runJavaScript(js, function(result) {console.log(result); });
}
