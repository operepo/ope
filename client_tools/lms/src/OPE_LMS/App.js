.pragma library

//var current_course = "";
//var current_course_name = "";
//var current_page_url = "";


var section_text_color = "#032569";
var section_bg_color = "#dbdbdb";
var text_color = "#032569";
var bg_color = "#ededed";
var bg_color2 = "white";
var highlight_color = "lightsteelblue";
var highlight_color2 = "#f5f5f5";

// JS Script needed to inject into webviews
var WebChannelJS = "<script src='http://localhost:65525/opeWebViewClient.js' type='text/javascript'></script>";


function findRecord(model, field_name, value) {
    // Find the first record with this field=value
    var ret = undefined;

    if (model === undefined) {
        console.log("findRecord - No model sent?");
        return ret;
    }
    if (model.getColumnIndex === undefined) {
        return ret;
    }

    // Loop until we find the record
    for (var i = 0; model.rowCount(); i++) {
        var v = getFieldValue(model, i, field_name, undefined);
        if (v === value) {
            ret = v;
            return ret;
        }

    }

    return ret;
}

function getFieldValue(model, row, field_name, default_value) {
    if (default_value === undefined) {
        default_value = "";
    }
    var ret = default_value;
    if (model === undefined){
        console.log("Error! bad model " + field_name );
        return ret;
    }
    if (model.getColumnIndex === undefined) {
        return ret;
    }

    var i =  model.getColumnIndex(field_name);
    var index = model.index(row, i);
    ret = model.data(index, Qt.DisplayRole);

    if (ret === undefined) {
        ret = "";
    }

    return ret;
}

function setHTML(wView, html) {
    // Use JS to write out the HTML to the web engine
    // Stupid hack because QT didn't provide this

    var js = "document.body.innerHTML=`" + html.replace("`", "\`") + "`";
    wView.runJavaScript(js, function(result) {console.log(result); });
}

function format_participants(json_str) {
    if (json_str === undefined) {
        return "";
    }
    if (json_str === "") {
        return "";
    }

    //console.log("Parsing: " + json_str);
    var p = JSON.parse(json_str);

    var ret = "";

    for (var i = 0; i < p.length; i++) {
        var curr_item = p[i];
        if (ret !== "") {
            ret += ", ";
        }
        ret += curr_item.full_name;
    }

    return ret;
}
