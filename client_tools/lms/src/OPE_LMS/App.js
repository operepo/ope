.pragma library

//var current_course = "";
//var current_course_name = "";
//var current_page_url = "";

var global_sidebar_bg_color = "#394b58";
var course_sidebar_bg_color = "#ffffff";

var global_primary_brand_color = "#0374b5";
var global_main_text_color = "#2d3b45";
var global_link_color = "#0374b5";
var global_primary_button = "#0374b5";
var global_primary_button_text = "#ffffff";
var global_secondary_button = "#2d3b45";
var global_secondary_button_text = "#ffffff";

var global_nav_background = "#394b58";
var global_nav_background_active = "#ffffff";
var global_nav_background_hover = "#2d3b45";
var global_nav_icon = "#ffffff";
var global_nav_icon_active = "#0374b5";
var global_nav_text = "#ffffff";
var global_nav_text_active = "#0374b5";
var global_nav_avatar_border = "#ffffff";
var global_nav_badge = "#ffffff";
var global_nav_badge_active = "#0374b5";
var global_nav_badge_text = "#000000";
var global_nav_badge_text_active = "#ffffff";
var global_nav_logo_background = "#394b58";

var module_bg_color = "#f5f5f5";
var module_text_color = "#3d454c";
var module_item_bg_color = "#ffffff";
var module_item_text = "#2d3b45";

var global_font_family = "Lato Extended, Lato, Helvetica Nueue";
var global_font_size = "14";

var page_bg_color = "#ffffff";
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
